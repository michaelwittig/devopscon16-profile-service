default: test

npm-dev:
	@echo "npm-dev"
	@rm -rf node_modules/
	@npm install
	@echo

npm:
	@echo "npm"
	@rm -rf node_modules/
	@npm install --production
	@echo

jshint:
	@echo "jshint"
	@find . -name "*.js" -print0 | xargs -0 ./node_modules/.bin/jshint
	@echo

mocha:
	@echo "mocha"
	@./node_modules/.bin/mocha test/*.js
	@echo

test: jshint mocha
	@echo "test"
	@echo
