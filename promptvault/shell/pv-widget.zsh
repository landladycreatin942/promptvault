# promptvault zsh widget — paste previous prompts into the command line
# Usage: eval "$(promptvault shell-init zsh)"

__promptvault_widget() {
  local selected
  selected=$(promptvault _fzf-widget-lines 2>/dev/null | \
    fzf --scheme=history --height=40% --layout=reverse \
        --prompt="pv> " --no-multi \
        --delimiter=$'\t' --with-nth=2 \
        --preview-window=hidden)
  if [[ -n "$selected" ]]; then
    LBUFFER="${LBUFFER}$(echo "$selected" | cut -f2)"
  fi
  zle reset-prompt
}
zle -N __promptvault_widget
bindkey "${PROMPTVAULT_WIDGET_KEY:-\ep}" __promptvault_widget
