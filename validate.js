const fs = require('fs');

const checks = {
  'site.css': {
    file: '/home/kellogg/dev/rogue_routine/static/css/site.css',
    patterns: [
      { name: 'skip-link styles', regex: /\.skip-link\s*\{\s*position:\s*absolute/ },
      { name: 'nav-brand margin-right auto', regex: /\.nav-brand\s*\{[^}]*margin-right:\s*auto/ },
      { name: 'digest card opacity 0.9', regex: /\.digest-card:nth-of-type\(3\)\s*\{\s*opacity:\s*0\.9/ },
      { name: 'article-source data-source selector', regex: /\.article-source\[data-source\]\s*\{/ },
      { name: 'score-tooltip visible class', regex: /\.score-tooltip\.visible\s*\{\s*display:\s*block/ },
      { name: 'reader-status-row styles', regex: /\.reader-status-row\s*\{\s*display:\s*flex/ },
      { name: 'domain-grid styles', regex: /\.domain-grid\s*\{\s*display:\s*grid/ },
      { name: 'print stylesheet', regex: /@media\s+print/ },
    ]
  },
  'reader.js': {
    file: '/home/kellogg/dev/rogue_routine/static/js/reader.js',
    patterns: [
      { name: 'elClearFilters variable', regex: /var elClearFilters = document\.getElementById\("clear-filters"\)/ },
      { name: 'onClearFilters function', regex: /function onClearFilters\(\)/ },
      { name: 'hasActiveFilters function', regex: /function hasActiveFilters\(\)/ },
      { name: 'updateClearButton function', regex: /function updateClearButton\(\)/ },
      { name: 'setSourceFilter function', regex: /function setSourceFilter\(/ },
      { name: 'clear-filters event listener', regex: /elClearFilters\.addEventListener\("click",\s*onClearFilters\)/ },
      { name: 'updateClearButton in render', regex: /function render\(\)[^}]*updateClearButton\(\)/ },
      { name: 'tooltip toggle via visible class', regex: /tooltip\.classList\.toggle\("visible"\)/ },
      { name: 'scrollIntoView on pagination', regex: /elList\.scrollIntoView\(\s*\{\s*behavior:\s*"smooth"/ },
    ]
  }
};

let failedTests = [];
let passedTests = [];

Object.entries(checks).forEach(([name, { file, patterns }]) => {
  try {
    const content = fs.readFileSync(file, 'utf8');
    patterns.forEach(({ name: testName, regex }) => {
      if (regex.test(content)) {
        passedTests.push(`${name}: ${testName}`);
      } else {
        failedTests.push(`${name}: ${testName}`);
      }
    });
  } catch (e) {
    failedTests.push(`${name}: ${e.message}`);
  }
});

console.log(`PASSED: ${passedTests.length}`);
if (failedTests.length > 0) {
  console.log(`FAILED: ${failedTests.length}`);
  failedTests.forEach(t => console.log(`  ✗ ${t}`));
  process.exit(1);
} else {
  console.log(`✓ All ${passedTests.length} checks passed`);
}
