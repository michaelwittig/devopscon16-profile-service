"use strict";

var config = require("./config.json");
var AWS = require("aws-sdk");
var dynamodb = new AWS.DynamoDB();
var lambda = new AWS.Lambda();

exports.handler = function(event, context, cb) {
  console.log(JSON.stringify(event));
  lambda.invoke({
    "FunctionName": config.LocationLambdaArn,
    "InvocationType": "RequestResponse",
    "Payload": JSON.stringify({"id": event.id, "action": "get"})
  }, function(err, data) {
    if (err) {
      cb(err);
    } else {
      console.log(JSON.stringify(data));
      if (data.FunctionError === undefined) {
        var location = JSON.parse(data.Payload);
        dynamodb.getItem({
          "Key": {
            "id": {
              "S": event.id
            }
          },
          "TableName": "profile"
        }, function(err, data) {
          if (err) {
            cb(err);
          } else {
            console.log(JSON.stringify(data));
            if (data.Item === undefined) {
              cb(new Error("ServiceErrorNotFound"));
            } else {
              cb(null, {
                "status": 200,
                "body": {
                  "id": data.Item.id.S,
                  "label": data.Item.label.S,
                  "location": {
                    "latitude": location.body.latitude,
                    "longitude": location.body.longitude
                  }
                }
              });
            }
          }
        });
      } else {
        cb(new Error(data.FunctionError + ": " + data.Payload));
      }
    }
  });
};
