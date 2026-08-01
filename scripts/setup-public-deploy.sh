#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-$(git config --get remote.origin.url | sed -E 's#git@github.com:#https://github.com/#; s#https://github.com/##; s#\.git$##')}"

if [ -z "${REPO}" ]; then
  echo "Could not detect GitHub repository from the current git remote." >&2
  exit 1
fi

if [ $# -lt 1 ]; then
  echo "Usage: $0 <render-deploy-hook-url> [vercel-token] [vercel-org-id] [vercel-project-id] [vite-api-base-url] [vite-app-name]" >&2
  exit 1
fi

RENDER_DEPLOY_HOOK_URL="${1:-}"
VERCEL_TOKEN="${2:-}"
VERCEL_ORG_ID="${3:-}"
VERCEL_PROJECT_ID="${4:-}"
VITE_API_BASE_URL="${5:-}"
VITE_APP_NAME="${6:-Hosamahad Platform}"

if [ -n "$RENDER_DEPLOY_HOOK_URL" ]; then
  gh secret set RENDER_DEPLOY_HOOK_URL --repo "$REPO" --body "$RENDER_DEPLOY_HOOK_URL"
fi

if [ -n "$VERCEL_TOKEN" ]; then
  gh secret set VERCEL_TOKEN --repo "$REPO" --body "$VERCEL_TOKEN"
fi

if [ -n "$VERCEL_ORG_ID" ]; then
  gh secret set VERCEL_ORG_ID --repo "$REPO" --body "$VERCEL_ORG_ID"
fi

if [ -n "$VERCEL_PROJECT_ID" ]; then
  gh secret set VERCEL_PROJECT_ID --repo "$REPO" --body "$VERCEL_PROJECT_ID"
fi

if [ -n "$VITE_API_BASE_URL" ]; then
  gh variable set VITE_API_BASE_URL --repo "$REPO" --body "$VITE_API_BASE_URL"
fi

if [ -n "$VITE_APP_NAME" ]; then
  gh variable set VITE_APP_NAME --repo "$REPO" --body "$VITE_APP_NAME"
fi

echo "Deployment configuration applied to $REPO"
