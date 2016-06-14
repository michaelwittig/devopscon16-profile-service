"use strict";

var config = require("./config.json");
var AWS = require("aws-sdk");
var dynamodb = new AWS.DynamoDB();
var lambda = new AWS.Lambda();

exports.handler = function(event, context, cb) {
  console.log(JSON.stringify(event));
  dynamodb.getItem({
    "Key": {
      "id": {
        "S": event.id
      }
    },
    "TableName": "profile"
  }, function(err, data1) {
    if (err) {
      cb(err);
    } else {
      console.log(JSON.stringify(data1));
      if (data1.Item === undefined) {
        cb(new Error("[NotFound] Profile not found"));
      } else {
        lambda.invoke({
          "FunctionName": config.LocationLambdaArn,
          "InvocationType": "RequestResponse",
          "Payload": JSON.stringify({"id": event.id, "action": "get"})
        }, function(err, data2) {
          if (err) {
            cb(err);
          } else {
            console.log(JSON.stringify(data2));
            if (data2.FunctionError === undefined) {
              var location = JSON.parse(data2.Payload);
              cb(null, {
                "body": {
                  "id": data1.Item.id.S,
                  "label": data1.Item.label.S,
                  "location": {
                    "latitude": location.body.latitude,
                    "longitude": location.body.longitude
                  }
                }
              });
            } else {
              cb(new Error("[InternalServerError] " + data2.FunctionError + ": " + data2.Payload));
            }
          }
        });
      }
    }
  });
};
