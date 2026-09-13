ARCHIVE ?= ../pcg-v3-github-reproduction-20260913-v8.7z

.PHONY: reproduce verify-release verify-profile

reproduce:
	TZ=UTC python3 scripts/reproduce_public_release.py --archive "$(ARCHIVE)"

verify-release:
	TZ=UTC python3 tools/VERIFY_ARCHIVE.py verify --archive "$(ARCHIVE)" --public

verify-profile:
	TZ=UTC python3 scripts/verify_public_package_v6.py --archive "$(ARCHIVE)"
