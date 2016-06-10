"use strict";

exports.handler = function(event, context, cb) {
  console.log(JSON.stringify(event));
  cb({
    "body": {
      "id": event.id,
      "label": "test",
      "location": {
        "latitude": 0,
        "longitude": 0
      }
    }
  });
};
