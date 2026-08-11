.PHONY: release
release: ## cut a release from master: verify branches, cz bump, push master and the tag
	@branch=$$(git rev-parse --abbrev-ref HEAD); \
	if [ "$$branch" != "master" ]; then \
		echo "ERROR: releases are cut from master (currently on $$branch)"; exit 1; \
	fi
	@git fetch origin master develop
	@if [ "$$(git rev-parse master)" != "$$(git rev-parse origin/master)" ]; then \
		echo "ERROR: local master is not aligned with origin/master"; exit 1; \
	fi
	@if [ "$$(git rev-parse develop)" != "$$(git rev-parse origin/develop)" ]; then \
		echo "ERROR: local develop is not aligned with origin/develop"; exit 1; \
	fi
	@if ! git merge-base --is-ancestor develop master; then \
		echo "ERROR: develop has not been merged into master"; exit 1; \
	fi
	@uvx --from commitizen cz bump
	@tag=$$(git describe --tags --exact-match); \
	echo "Pushing master and tag $$tag"; \
	git push origin master "$$tag"

test-cov: ## run tests with coverage
	@pytest tests --junitxml=`pwd`/~build/pytest.xml -vv \
        --cov-report=xml:`pwd`/~build/coverage.xml --cov-report=html --cov-report=term \
        --cov-config=tests/.coveragerc \
        --cov=ktcalendars || true
	@if [ "${BROWSERCMD}" != "" ]; then \
    	"${BROWSERCMD}" `pwd`/~build/coverage/index.html ; \
    fi
