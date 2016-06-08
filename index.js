"use strict";

exports.handler = function(event, context) {
  console.log(JSON.stringify(event));
  context.succeed({});
};
