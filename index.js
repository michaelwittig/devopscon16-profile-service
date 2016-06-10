"use strict";

var AWS = require("aws-sdk");
var dynamodb = new AWS.DynamoDB();

exports.handler = function(event, context, cb) {
  console.log(JSON.stringify(event));
  var id = event.id;
  dynamodb.getItem({
    "Key": {
      "id": {
        "S": id
      }
    },
    "TableName": "profile"
  }, function(err, data) {
    if (err) {
      cb(err);
    } else {
      if (data.Item === undefined) {
        cb(new Error("ServiceErrorNotFound"));
      } else {
        console.log(JSON.stringify(data.Item));
        cb(null, {
          "status": 200,
          "body": {
            "id": data.Item.id.S,
            "label": data.Item.label.S,
            "location": {
              "latitude": data.Item.latitude.N,
              "longitude": data.Item.longitude.N
            }
          }
        });
      }
    }
  });
};
