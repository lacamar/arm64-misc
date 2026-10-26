lint:
    #!/bin/sh
    tools/check-specs || exit 1
    s=$(git diff --cached --name-only --diff-filter=AM -- '*.spec' ':!specfiles/wip')
    [ -z "$s" ] || rpmlint -c rpmlint.toml $s

test:
    git ls-files '*.spec' ':!specfiles/wip' | xargs rpmlint -c rpmlint.toml
