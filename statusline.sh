#!/usr/bin/env bash
# Claude Code statusline — SecondBrain 客製版
# 使用 Python 解析 JSON（Windows 環境無 jq）

input=$(cat)

# --- ANSI colors ---
RESET="\033[0m"
BOLD="\033[1m"
DIM="\033[2m"
RED="\033[31m"
YELLOW="\033[33m"
GREEN="\033[32m"
CYAN="\033[36m"
MAGENTA="\033[35m"

# --- 用 Python 解析所有 JSON 欄位，輸出為 shell 變數 ---
eval "$(echo "$input" | python -c "
import json, sys, math

try:
    d = json.load(sys.stdin)
except:
    d = {}

def g(obj, *keys, default=''):
    for k in keys:
        if isinstance(obj, dict):
            obj = obj.get(k)
        else:
            return default
        if obj is None:
            return default
    return str(obj) if obj is not None else default

cw   = d.get('context_window', {})
cu   = cw.get('current_usage', {})
rl   = d.get('rate_limits', {})
fh   = rl.get('five_hour', {})
ws   = d.get('workspace', {})
mdl  = d.get('model', {})
cst  = d.get('cost', {})

project_dir   = g(ws, 'project_dir')
used_pct      = g(cw, 'used_percentage')
input_tokens  = g(cu, 'input_tokens',  default='0')
output_tokens = g(cu, 'output_tokens', default='0')
total_in      = g(cw, 'total_input_tokens',  default='0')
total_out     = g(cw, 'total_output_tokens', default='0')
cache_read    = g(cu, 'cache_read_input_tokens',    default='0')
cache_create  = g(cu, 'cache_creation_input_tokens',default='0')
quota_pct     = g(fh, 'used_percentage')
quota_reset   = g(fh, 'resets_at')
model_name    = g(mdl,'display_name') or 'Claude'
session_name  = g(d,  'session_name')
session_id    = g(d,  'session_id')
cost_usd      = g(cst, 'total_cost_usd', default='')

print(f'PY_PROJECT_DIR={repr(project_dir)}')
print(f'PY_USED_PCT={repr(used_pct)}')
print(f'PY_INPUT_TOKENS={repr(input_tokens)}')
print(f'PY_OUTPUT_TOKENS={repr(output_tokens)}')
print(f'PY_TOTAL_IN={repr(total_in)}')
print(f'PY_TOTAL_OUT={repr(total_out)}')
print(f'PY_CACHE_READ={repr(cache_read)}')
print(f'PY_CACHE_CREATE={repr(cache_create)}')
print(f'PY_QUOTA_PCT={repr(quota_pct)}')
print(f'PY_QUOTA_RESET={repr(quota_reset)}')
print(f'PY_MODEL={repr(model_name)}')
print(f'PY_SESSION_NAME={repr(session_name)}')
print(f'PY_SESSION_ID={repr(session_id)}')
print(f'PY_COST_USD={repr(cost_usd)}')
" 2>/dev/null)"

# --- Git 分支 ---
git_branch=""
git_status_color="$GREEN"
if [ -n "$PY_PROJECT_DIR" ] && command -v git >/dev/null 2>&1; then
    git_branch=$(git -C "$PY_PROJECT_DIR" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ -n "$git_branch" ]; then
        git_conflict=$(git -C "$PY_PROJECT_DIR" --no-optional-locks diff --name-only --diff-filter=U 2>/dev/null)
        git_dirty=$(git -C "$PY_PROJECT_DIR" --no-optional-locks status --porcelain 2>/dev/null)
        if [ -n "$git_conflict" ]; then
            git_status_color="$RED"
        elif [ -n "$git_dirty" ]; then
            git_status_color="$YELLOW"
        fi
    fi
fi

# --- Context bar ---
ctx_display="${DIM}ctx: N/A${RESET}"
if [ -n "$PY_USED_PCT" ] && [ "$PY_USED_PCT" != "0" ]; then
    pct_int=$(printf "%.0f" "$PY_USED_PCT" 2>/dev/null || echo "0")
    filled=$(( pct_int / 10 ))
    [ "$filled" -gt 10 ] && filled=10
    empty=$(( 10 - filled ))
    bar=""
    for i in $(seq 1 $filled); do bar="${bar}█"; done
    for i in $(seq 1 $empty);  do bar="${bar}░"; done
    if [ "$pct_int" -ge 80 ]; then
        ctx_color="$RED"
    elif [ "$pct_int" -ge 50 ]; then
        ctx_color="$YELLOW"
    else
        ctx_color="$GREEN"
    fi
    ctx_display="${ctx_color}${bar} ${pct_int}%${RESET}"
fi

# --- Token 合計 ---
total_tokens=$(( PY_TOTAL_IN + PY_TOTAL_OUT )) 2>/dev/null || total_tokens=0
if [ "$total_tokens" -ge 1000 ]; then
    tok_display=$(awk "BEGIN { printf \"%.1fk\", $total_tokens/1000 }")
else
    tok_display="${total_tokens}"
fi

# --- Cache 命中率 ---
cache_display="${DIM}cache: -${RESET}"
cr=${PY_CACHE_READ:-0}
it=${PY_INPUT_TOKENS:-0}
eligible=$(( it + cr )) 2>/dev/null || eligible=0
if [ "$eligible" -gt 0 ] && [ "$cr" -gt 0 ]; then
    cache_pct=$(awk "BEGIN { printf \"%.0f\", ($cr / $eligible) * 100 }")
    if   [ "$cache_pct" -ge 60 ]; then cache_color="$GREEN"
    elif [ "$cache_pct" -ge 30 ]; then cache_color="$YELLOW"
    else                               cache_color="$RED"; fi
    cache_display="${cache_color}cache: ${cache_pct}%${RESET}"
fi

# --- 配額倒數 ---
quota_display="${GREEN}quota: OK${RESET}"
if [ -n "$PY_QUOTA_PCT" ] && [ "$PY_QUOTA_PCT" != "0" ]; then
    q_int=$(printf "%.0f" "$PY_QUOTA_PCT" 2>/dev/null || echo "0")
    remaining=$(( 100 - q_int ))
    if [ -n "$PY_QUOTA_RESET" ] && [ "$PY_QUOTA_RESET" != "0" ]; then
        now=$(date +%s 2>/dev/null || echo "0")
        secs_left=$(( PY_QUOTA_RESET - now ))
        [ "$secs_left" -lt 0 ] && secs_left=0
        mins=$(( secs_left / 60 ))
        secs=$(( secs_left % 60 ))
        time_str=$(printf "%dm%02ds" "$mins" "$secs")
        if   [ "$q_int" -ge 90 ]; then q_color="$RED"
        elif [ "$q_int" -ge 70 ]; then q_color="$YELLOW"
        else                           q_color="$GREEN"; fi
        quota_display="${q_color}quota: ${remaining}% ⏱ ${time_str}${RESET}"
    else
        quota_display="${GREEN}quota: ${remaining}%${RESET}"
    fi
fi

# --- Session label ---
if [ -n "$PY_SESSION_NAME" ]; then
    session_label="$PY_SESSION_NAME"
elif [ -n "$PY_SESSION_ID" ]; then
    session_label="${PY_SESSION_ID:0:8}"
else
    session_label="?"
fi

# --- LINE 1: branch / context bar / model ---
line1=""
[ -n "$git_branch" ] && line1="${git_status_color}${BOLD} ${git_branch}${RESET}  "
line1="${line1}${ctx_display}  ${CYAN}${PY_MODEL}${RESET}  ${DIM}[${session_label}]${RESET}"

# --- Session cost ---
cost_display="${DIM}cost: -${RESET}"
if [ -n "$PY_COST_USD" ] && [ "$PY_COST_USD" != "0.0" ] && [ "$PY_COST_USD" != "0" ]; then
    cost_display="${CYAN}cost: \$$(printf "%.4f" "$PY_COST_USD")${RESET}"
fi

# --- LINE 2: quota / cache / tokens / cost ---
line2="${quota_display}   ${cache_display}   ${MAGENTA}tokens: ${tok_display}${RESET}   ${cost_display}"

line3=$(echo "$input" | ccusage statusline 2>/dev/null || true)

if [ -n "$line3" ]; then
    printf "%b\n%b\n%b\n" "${line1}" "${line2}" "${line3}"
else
    printf "%b\n%b\n" "${line1}" "${line2}"
fi
