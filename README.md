# DevOpsCon 2016: The Life of a Serverless Microservice on AWS

The profile service retrieves information about the user.

## Usage

```
curl -vvv "https://6jj2ko4wml.execute-api.us-east-1.amazonaws.com/v1/profile/123"

curl "https://6jj2ko4wml.execute-api.us-east-1.amazonaws.com/v1/profile/123" | python -m json.tool
```

## See also

* https://github.com/michaelwittig/devopscon16-auth-service
* https://github.com/michaelwittig/devopscon16-location-service
* https://github.com/michaelwittig/devopscon16-global
