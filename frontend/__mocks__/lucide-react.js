const React = require('react');

module.exports = {
  Coffee: () => React.createElement('div', { 'data-testid': 'coffee-icon' }),
  Skull: () => React.createElement('div', { 'data-testid': 'skull-icon' }),
  Terminal: () => React.createElement('div', { 'data-testid': 'terminal-icon' }),
  GitBranch: () => React.createElement('div', { 'data-testid': 'git-branch-icon' }),
  Code2: () => React.createElement('div', { 'data-testid': 'code-icon' }),
};
