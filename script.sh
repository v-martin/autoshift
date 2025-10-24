#!/bin/bash

set -e

show_usage() {
    echo "Usage: $0 REPO_PATH TARGET_PATH [OPTIONS]"
    echo ""
    echo "Required arguments:"
    echo "  REPO_PATH       Path to git repository (absolute or relative)"
    echo "  TARGET_PATH     Directory or file to remove (relative to repo root)"
    echo ""
    echo "Optional arguments:"
    echo "  -m MESSAGE      Commit message (default: 'Remove TARGET_PATH from all branches')"
    echo "  -d, --dry-run   Run in dry-run mode without pushing (default: false)"
    echo "  -y, --yes       Skip confirmation prompt (default: false)"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 /path/to/repo .github/workflows"
    echo "  $0 /path/to/repo .github/workflows -m 'Remove CI workflows' --dry-run"
    echo "  $0 /path/to/repo .vscode -y"
    exit 1
}

if [ $# -lt 2 ]; then
    echo "Error: Missing required arguments"
    echo ""
    show_usage
fi

REPO_PATH="$1"
TARGET_PATH="$2"
shift 2

COMMIT_MESSAGE=""

while [ $# -gt 0 ]; do
    case "$1" in
        -m)
            COMMIT_MESSAGE="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            echo "Error: Unknown option: $1"
            echo ""
            show_usage
            ;;
    esac
done

if [ -z "$COMMIT_MESSAGE" ]; then
    COMMIT_MESSAGE="Remove ${TARGET_PATH} from all branches"
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW} $1${NC}"
}

print_error() {
    echo -e "${RED} $1${NC}"
}

print_info() {
    echo -e "${BLUE} $1${NC}"
}

validate_inputs() {
    print_header "Validating inputs"

    if [ ! -d "$REPO_PATH" ]; then
        print_error "Repository path does not exist: $REPO_PATH"
        exit 1
    fi

    if [ ! -d "$REPO_PATH/.git" ]; then
        print_error "Not a git repository: $REPO_PATH"
        exit 1
    fi

    print_success "Repository path is valid: $REPO_PATH"

    if [ -z "$TARGET_PATH" ]; then
        print_error "Target path is not specified"
        exit 1
    fi

    print_success "Target path: $TARGET_PATH"
    echo ""
}


main() {
    validate_inputs

    cd "$REPO_PATH"

    print_header "Configuration"
    echo "Repository: $REPO_PATH"
    echo "Target: $TARGET_PATH"
    echo "Commit message: $COMMIT_MESSAGE"
    echo ""

    ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    print_info "Current branch: $ORIGINAL_BRANCH"

    if ! git diff --quiet || ! git diff --quiet --cached; then
        echo ""
        print_warning "Working directory has uncommitted changes:"
        git status --short
        echo ""
        print_error "Please commit or stash your changes before running this script"
        print_info "Run: git stash"
        exit 1
    fi

    print_info "Fetching latest changes..."
    git fetch --all --quiet 2>/dev/null || git fetch --all

    print_info "Getting list of all branches..."
    ALL_BRANCHES=$(git branch -r | grep -v '\->' | sed 's/origin\///' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | sort -u)

    BRANCH_COUNT=$(echo "$ALL_BRANCHES" | wc -l)
    print_success "Found $BRANCH_COUNT branches"
    echo ""

    print_header "Branches to process"
    echo "$ALL_BRANCHES"
    echo ""

    print_warning "This will remove '$TARGET_PATH' from ALL branches listed above."

    echo ""
    read -p "Do you want to continue? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        print_info "Operation cancelled by user"
        exit 0
    fi

    echo ""
    print_header "Processing branches"

    PROCESSED=0
    SKIPPED=0
    ERRORS=0

    while IFS= read -r BRANCH; do
        BRANCH=$(echo "$BRANCH" | xargs)
        [ -z "$BRANCH" ] && continue

        echo ""
        print_info "Processing branch: $BRANCH"

        if git checkout "$BRANCH" 2>/dev/null; then
            :
        elif git checkout -b "$BRANCH" "origin/$BRANCH" 2>/dev/null; then
            print_info "Created local branch tracking origin/$BRANCH"
        else
            print_error "Failed to checkout branch: $BRANCH"
            ((ERRORS++))
            continue
        fi

        if ! git pull origin "$BRANCH" --quiet 2>/dev/null; then
            print_warning "Failed to pull branch: $BRANCH (continuing anyway)"
        fi

        if [ ! -e "$TARGET_PATH" ]; then
            print_warning "Target '$TARGET_PATH' does not exist in branch '$BRANCH' - skipping"
            ((SKIPPED++))
            continue
        fi

        if [ -d "$TARGET_PATH" ]; then
            print_info "Removing directory: $TARGET_PATH"
            git rm -rf "$TARGET_PATH" --quiet
        else
            print_info "Removing file: $TARGET_PATH"
            git rm -f "$TARGET_PATH" --quiet
        fi

        if ! git diff --quiet --cached; then
            git commit -m "$COMMIT_MESSAGE"
            print_success "Committed changes"

            if git push origin "$BRANCH"; then
                print_success "Pushed branch: $BRANCH"
                ((PROCESSED++))
            else
                print_error "Failed to push branch: $BRANCH"
                ((ERRORS++))
            fi
        else
            print_warning "No changes detected (target might be already removed)"
            ((SKIPPED++))
        fi

    done <<< "$ALL_BRANCHES"

    echo ""
    print_info "Returning to original branch: $ORIGINAL_BRANCH"
    git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true

    echo ""
    print_header "Summary"
    echo "Total branches: $BRANCH_COUNT"
    print_success "Processed: $PROCESSED"
    print_warning "Skipped: $SKIPPED"
    if [ $ERRORS -gt 0 ]; then
        print_error "Errors: $ERRORS"
    else
        print_success "Errors: 0"
    fi

    echo ""
    print_success "All done! Changes have been pushed to remote repository."

}

main "$@"

