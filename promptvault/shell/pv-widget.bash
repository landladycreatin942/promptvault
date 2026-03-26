# promptvault bash widget — paste previous prompts into the command line
# Usage: eval "$(promptvault shell-init bash)"

__promptvault_widget() {
  local selected
  selected=$(promptvault _fzf-widget-lines 2>/dev/null | \
    fzf --scheme=history --height=40% --layout=reverse \
        --prompt="pv> " --no-multi \
        --delimiter=$'\t' --with-nth=2 \
        --preview-window=hidden)
  if [[ -n "$selected" ]]; then
    READLINE_LINE="${READLINE_LINE}$(echo "$selected" | cut -f2)"
    READLINE_POINT=${#READLINE_LINE}
  fi
}
bind -x '"${PROMPTVAULT_WIDGET_KEY:-\ep}": __promptvault_widget'
