/**
 * GIVC Healthcare Platform - Logger Migration Script
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Automated script to replace console.log calls with HIPAA-compliant logger
 * Usage: node scripts/migrate-to-logger.js
 */

const fs = require('fs');
const path = require('path');

const FRONTEND_SRC = path.join(__dirname, '../frontend/src');
const WORKERS_SRC = path.join(__dirname, '../workers');

// Files to skip (already using logger or system files)
const SKIP_FILES = [
  'logger.js',
  'logger.ts',
  'validateEnv.js',
  'validateEnv.ts',
  'main.tsx',
  'main.jsx',
];

// Track statistics
const stats = {
  filesProcessed: 0,
  filesModified: 0,
  consoleLogsReplaced: 0,
  consoleWarnsReplaced: 0,
  consoleErrorsReplaced: 0,
  files: [],
};

/**
 * Check if file should be processed
 */
function shouldProcessFile(filePath) {
  const fileName = path.basename(filePath);
  const ext = path.extname(filePath);
  
  // Only process JS/TS/JSX/TSX files
  if (!['.js', '.ts', '.jsx', '.tsx'].includes(ext)) {
    return false;
  }
  
  // Skip specific files
  if (SKIP_FILES.includes(fileName)) {
    return false;
  }
  
  // Skip node_modules and dist
  if (filePath.includes('node_modules') || filePath.includes('dist')) {
    return false;
  }
  
  return true;
}

/**
 * Process a single file
 */
function processFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    let modified = false;
    let fileStats = {
      path: filePath,
      logs: 0,
      warns: 0,
      errors: 0,
    };
    
    // Check if logger is already imported
    const hasLoggerImport = /import\s+.*logger.*from\s+['"].*logger/i.test(content);
    
    // Count console calls
    const consoleLogCount = (content.match(/console\.log\(/g) || []).length;
    const consoleWarnCount = (content.match(/console\.warn\(/g) || []).length;
    const consoleErrorCount = (content.match(/console\.error\(/g) || []).length;
    
    if (consoleLogCount === 0 && consoleWarnCount === 0 && consoleErrorCount === 0) {
      return false; // No changes needed
    }
    
    // Add logger import if not present
    if (!hasLoggerImport) {
      // Determine correct import path
      const isWorker = filePath.includes('workers');
      const relativePath = isWorker
        ? './services/logger' // Adjust based on file location
        : '@/services/logger';
      
      // Find the last import statement
      const importRegex = /^import\s+.*from\s+['"].*['"];?\s*$/gm;
      const imports = content.match(importRegex);
      
      if (imports && imports.length > 0) {
        const lastImport = imports[imports.length - 1];
        const lastImportIndex = content.lastIndexOf(lastImport);
        const insertPosition = lastImportIndex + lastImport.length;
        
        content = 
          content.slice(0, insertPosition) + 
          `\nimport logger from '${relativePath}';\n` + 
          content.slice(insertPosition);
        
        modified = true;
      }
    }
    
    // Replace console.log with logger.info
    if (consoleLogCount > 0) {
      content = content.replace(/console\.log\(/g, 'logger.info(');
      fileStats.logs = consoleLogCount;
      stats.consoleLogsReplaced += consoleLogCount;
      modified = true;
    }
    
    // Replace console.warn with logger.warn
    if (consoleWarnCount > 0) {
      content = content.replace(/console\.warn\(/g, 'logger.warn(');
      fileStats.warns = consoleWarnCount;
      stats.consoleWarnsReplaced += consoleWarnCount;
      modified = true;
    }
    
    // Replace console.error with logger.error
    if (consoleErrorCount > 0) {
      content = content.replace(/console\.error\(/g, 'logger.error(');
      fileStats.errors = consoleErrorCount;
      stats.consoleErrorsReplaced += consoleErrorCount;
      modified = true;
    }
    
    // Write back if modified
    if (modified && content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      stats.filesModified++;
      stats.files.push(fileStats);
      return true;
    }
    
    return false;
  } catch (error) {
    console.error(`Error processing ${filePath}:`, error.message);
    return false;
  }
}

/**
 * Recursively process directory
 */
function processDirectory(dir) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      processDirectory(filePath);
    } else if (shouldProcessFile(filePath)) {
      stats.filesProcessed++;
      processFile(filePath);
    }
  });
}

/**
 * Main execution
 */
function main() {
  console.log('🚀 GIVC Logger Migration Tool\n');
  console.log('Starting console.log → logger migration...\n');
  
  // Process frontend
  if (fs.existsSync(FRONTEND_SRC)) {
    console.log('📂 Processing frontend/src...');
    processDirectory(FRONTEND_SRC);
  }
  
  // Process workers
  if (fs.existsSync(WORKERS_SRC)) {
    console.log('📂 Processing workers...');
    processDirectory(WORKERS_SRC);
  }
  
  // Print results
  console.log('\n✅ Migration Complete!\n');
  console.log('📊 Statistics:');
  console.log(`   Files Processed: ${stats.filesProcessed}`);
  console.log(`   Files Modified: ${stats.filesModified}`);
  console.log(`   console.log → logger.info: ${stats.consoleLogsReplaced}`);
  console.log(`   console.warn → logger.warn: ${stats.consoleWarnsReplaced}`);
  console.log(`   console.error → logger.error: ${stats.consoleErrorsReplaced}`);
  console.log(`   Total Replacements: ${stats.consoleLogsReplaced + stats.consoleWarnsReplaced + stats.consoleErrorsReplaced}\n`);
  
  if (stats.filesModified > 0) {
    console.log('📝 Modified Files:');
    stats.files.forEach(file => {
      const relativePath = path.relative(process.cwd(), file.path);
      console.log(`   ${relativePath}`);
      if (file.logs > 0) console.log(`      ├─ ${file.logs} logger.info()`);
      if (file.warns > 0) console.log(`      ├─ ${file.warns} logger.warn()`);
      if (file.errors > 0) console.log(`      └─ ${file.errors} logger.error()`);
    });
  }
  
  console.log('\n🎉 All console calls have been replaced with HIPAA-compliant logger!');
  console.log('💡 Remember to review the changes and test your application.\n');
}

// Run migration
main();
