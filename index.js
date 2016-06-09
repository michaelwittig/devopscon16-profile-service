"use strict";

exports.handler = function(event, context, cb) {
  console.log(JSON.stringify(event));
  cb({});
};
