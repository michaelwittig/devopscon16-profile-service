import boto3
import botocore
import zipfile
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getStackOutput(stackName, outputKey):
  cfnClient = boto3.client('cloudformation')
  res = cfnClient.describe_stacks(StackName=stackName)
  outputs = res['Stacks'][0]['Outputs']
  logger.info('outputs:{}'.format(outputs))
  output = [x for x in outputs if x['OutputKey'] == outputKey][0]
  return output['OutputValue']

def extractTemplate(zipFile, sourceFile, destinationDir):
  found = False
  try:
    f = open(zipFile, 'rb')
    z = zipfile.ZipFile(f)
    for name in z.namelist():
      if name == sourceFile:
        z.extract(name, destinationDir)
        found = True
  finally:
    f.close()
  if found == False:
    raise Exception('sourceFile not found in zipFile')

def readFile(file):
  try:
    f = open(file, 'r')
    return f.read()
  finally:
    f.close()

def jobDone(jobId, context, data):
  logger.error('jobDone:{}'.format(data))
  cpClient = boto3.client('codepipeline')
  cpClient.put_job_success_result(jobId=jobId)

def jobFailed(jobId, context, message):
  logger.error('jobFailed:{}'.format(message))
  cpClient = boto3.client('codepipeline')
  cpClient.put_job_failure_result(
    jobId=jobId,
    failureDetails={
        'type': 'JobFailed',
        'message': message,
        'externalExecutionId': context.aws_request_id
    })

def existsStack(stackName):
  cfnClient = boto3.client('cloudformation')
  try:
    stack = cfnClient.describe_stacks(StackName=stackName)
    return True
  except botocore.exceptions.ClientError as e:
    return False

def updateStack(stackName, templateFile, s3Location):
  cfnClient = boto3.client('cloudformation')
  cfnClient.update_stack(
    StackName=stackName,
    TemplateBody=readFile(templateFile),
    Parameters=[
      {
        'ParameterKey': 'CodeS3Bucket',
        'ParameterValue': s3Location['bucketName']
      },
      {
        'ParameterKey': 'AlertTopicArn',
        'ParameterValue': getStackOutput('global', 'AlertTopicArn')
      },
      {
        'ParameterKey': 'LocationLambdaArn',
        'ParameterValue': getStackOutput('location-service', 'LocationLambdaArn')
      },
      {
        'ParameterKey': 'CodeS3Key',
        'ParameterValue': s3Location['objectKey']
      }
    ],
    Capabilities=['CAPABILITY_IAM']
  )
  cfnClient.get_waiter('stack_update_complete').wait(
    StackName=stackName,
  )

def createStack(stackName, templateFile, s3Location):
  cfnClient = boto3.client('cloudformation')
  cfnClient.create_stack(
    StackName=stackName,
    TemplateBody=readFile(templateFile),
    Parameters=[
      {
        'ParameterKey': 'CodeS3Bucket',
        'ParameterValue': s3Location['bucketName']
      },
      {
        'ParameterKey': 'AlertTopicArn',
        'ParameterValue': getStackOutput('global', 'AlertTopicArn')
      },
      {
        'ParameterKey': 'LocationLambdaArn',
        'ParameterValue': getStackOutput('location-service', 'LocationLambdaArn')
      },
      {
        'ParameterKey': 'CodeS3Key',
        'ParameterValue': s3Location['objectKey']
      }
    ],
    Capabilities=['CAPABILITY_IAM']
  )
  cfnClient.get_waiter('stack_create_complete').wait(
    StackName=stackName,
  )

def handler(event, context):
  logger.info('handler:{}'.format(event))
  jobId = event['CodePipeline.job']['id']
  try:
    artifactCredentials = event['CodePipeline.job']['data']['artifactCredentials']
    inputArtifact = event['CodePipeline.job']['data']['inputArtifacts'][0]
    s3Location = inputArtifact['location']['s3Location']
    s3Client = boto3.client(
      's3',
      aws_access_key_id=artifactCredentials['accessKeyId'],
      aws_secret_access_key=artifactCredentials['secretAccessKey'],
      aws_session_token=artifactCredentials['sessionToken'],
      config=botocore.client.Config(signature_version='s3v4'),
    )
    s3Client.download_file(s3Location['bucketName'], s3Location['objectKey'], '/tmp/artifact.zip')
    extractTemplate('/tmp/artifact.zip', 'service.json', '/tmp/')
    if existsStack('profile-service'):
      updateStack('profile-service', '/tmp/service.json', s3Location)
    else:
      createStack('profile-service', '/tmp/service.json', s3Location)
    jobDone(jobId, context, 'done')
  except Exception as e:
    logger.error('exception:{}'.format(event))
    jobFailed(jobId, context, str(e))
  return {}