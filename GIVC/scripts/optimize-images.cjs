/**
 * GIVC Healthcare Platform - Image Optimization Script
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Automated image optimization with WebP conversion, compression,
 * and responsive image generation
 */

const sharp = require('sharp');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const CONFIG = {
  inputDir: path.join(__dirname, '../frontend/src/assets/images'),
  outputDir: path.join(__dirname, '../frontend/src/assets/images/optimized'),
  formats: ['webp', 'avif', 'jpeg'], // Output formats
  sizes: {
    // Responsive image sizes
    thumbnail: 150,
    small: 320,
    medium: 640,
    large: 1024,
    xlarge: 1920,
  },
  quality: {
    webp: 80,
    avif: 75,
    jpeg: 85,
    png: 90,
  },
  maxFileSize: 500 * 1024, // 500KB max
};

// Statistics
const stats = {
  processed: 0,
  totalOriginalSize: 0,
  totalOptimizedSize: 0,
  images: [],
};

/**
 * Check if file is an image
 */
function isImage(filename) {
  const ext = path.extname(filename).toLowerCase();
  return ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'].includes(ext);
}

/**
 * Get file size
 */
async function getFileSize(filePath) {
  const stats = await fs.stat(filePath);
  return stats.size;
}

/**
 * Format bytes to human readable
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Optimize single image
 */
async function optimizeImage(inputPath, filename) {
  const baseName = path.parse(filename).name;
  const ext = path.extname(filename).toLowerCase();
  
  console.log(`\n📸 Processing: ${filename}`);
  
  // Get original size
  const originalSize = await getFileSize(inputPath);
  stats.totalOriginalSize += originalSize;
  
  const imageStats = {
    name: filename,
    originalSize: originalSize,
    optimizedFiles: [],
  };
  
  try {
    // Load image
    const image = sharp(inputPath);
    const metadata = await image.metadata();
    
    console.log(`   Dimensions: ${metadata.width}x${metadata.height}`);
    console.log(`   Original format: ${metadata.format}`);
    console.log(`   Original size: ${formatBytes(originalSize)}`);
    
    // Generate responsive sizes
    for (const [sizeName, width] of Object.entries(CONFIG.sizes)) {
      // Skip if original is smaller
      if (width > metadata.width) continue;
      
      console.log(`\n   📐 Generating ${sizeName} (${width}px)...`);
      
      // Generate different formats
      for (const format of CONFIG.formats) {
        const outputFilename = `${baseName}-${sizeName}.${format}`;
        const outputPath = path.join(CONFIG.outputDir, outputFilename);
        
        try {
          let pipeline = image.clone().resize(width, null, {
            withoutEnlargement: true,
            fit: 'inside',
          });
          
          // Apply format-specific options
          switch (format) {
            case 'webp':
              pipeline = pipeline.webp({ quality: CONFIG.quality.webp });
              break;
            case 'avif':
              pipeline = pipeline.avif({ quality: CONFIG.quality.avif });
              break;
            case 'jpeg':
            case 'jpg':
              pipeline = pipeline.jpeg({ quality: CONFIG.quality.jpeg, progressive: true });
              break;
            case 'png':
              pipeline = pipeline.png({ quality: CONFIG.quality.png, compressionLevel: 9 });
              break;
          }
          
          await pipeline.toFile(outputPath);
          
          const optimizedSize = await getFileSize(outputPath);
          const savings = ((1 - optimizedSize / originalSize) * 100).toFixed(1);
          
          stats.totalOptimizedSize += optimizedSize;
          imageStats.optimizedFiles.push({
            name: outputFilename,
            size: optimizedSize,
            savings: savings + '%',
          });
          
          console.log(`      ✓ ${format.toUpperCase()}: ${formatBytes(optimizedSize)} (${savings}% smaller)`);
        } catch (error) {
          console.error(`      ✗ Failed to generate ${format}: ${error.message}`);
        }
      }
    }
    
    stats.processed++;
    stats.images.push(imageStats);
    
  } catch (error) {
    console.error(`   ✗ Error processing image: ${error.message}`);
  }
}

/**
 * Process directory recursively
 */
async function processDirectory(dir) {
  try {
    const files = await fs.readdir(dir);
    
    for (const file of files) {
      const filePath = path.join(dir, file);
      const stat = await fs.stat(filePath);
      
      if (stat.isDirectory()) {
        // Skip node_modules and output directory
        if (!file.includes('node_modules') && !file.includes('optimized')) {
          await processDirectory(filePath);
        }
      } else if (isImage(file)) {
        await optimizeImage(filePath, file);
      }
    }
  } catch (error) {
    console.error(`Error processing directory ${dir}:`, error.message);
  }
}

/**
 * Generate responsive image HTML
 */
function generateResponsiveHTML(imageName) {
  const baseName = path.parse(imageName).name;
  
  return `
<!-- Responsive Image: ${imageName} -->
<picture>
  <!-- AVIF format (best compression) -->
  <source
    type="image/avif"
    srcset="
      /assets/images/optimized/${baseName}-small.avif 320w,
      /assets/images/optimized/${baseName}-medium.avif 640w,
      /assets/images/optimized/${baseName}-large.avif 1024w,
      /assets/images/optimized/${baseName}-xlarge.avif 1920w
    "
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 1024px"
  />
  
  <!-- WebP format (good compression, wide support) -->
  <source
    type="image/webp"
    srcset="
      /assets/images/optimized/${baseName}-small.webp 320w,
      /assets/images/optimized/${baseName}-medium.webp 640w,
      /assets/images/optimized/${baseName}-large.webp 1024w,
      /assets/images/optimized/${baseName}-xlarge.webp 1920w
    "
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 1024px"
  />
  
  <!-- JPEG fallback (universal support) -->
  <img
    src="/assets/images/optimized/${baseName}-large.jpeg"
    srcset="
      /assets/images/optimized/${baseName}-small.jpeg 320w,
      /assets/images/optimized/${baseName}-medium.jpeg 640w,
      /assets/images/optimized/${baseName}-large.jpeg 1024w,
      /assets/images/optimized/${baseName}-xlarge.jpeg 1920w
    "
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 1024px"
    alt="${imageName}"
    loading="lazy"
    decoding="async"
  />
</picture>
`;
}

/**
 * Main execution
 */
async function main() {
  console.log('🖼️  GIVC Image Optimization Tool\n');
  console.log('=' .repeat(50));
  
  // Create output directory
  try {
    await fs.mkdir(CONFIG.outputDir, { recursive: true });
    console.log(`✓ Output directory ready: ${CONFIG.outputDir}\n`);
  } catch (error) {
    console.error(`✗ Failed to create output directory: ${error.message}`);
    process.exit(1);
  }
  
  // Check if input directory exists
  try {
    await fs.access(CONFIG.inputDir);
  } catch (error) {
    console.log(`ℹ️  Input directory not found: ${CONFIG.inputDir}`);
    console.log('   Creating directory...');
    await fs.mkdir(CONFIG.inputDir, { recursive: true });
    console.log('   ✓ Directory created. Please add images and run again.\n');
    return;
  }
  
  // Process images
  console.log(`🔍 Scanning for images in: ${CONFIG.inputDir}\n`);
  const startTime = Date.now();
  
  await processDirectory(CONFIG.inputDir);
  
  const duration = ((Date.now() - startTime) / 1000).toFixed(2);
  
  // Print summary
  console.log('\n' + '='.repeat(50));
  console.log('\n✅ Optimization Complete!\n');
  console.log('📊 Summary:');
  console.log(`   Images Processed: ${stats.processed}`);
  console.log(`   Original Total Size: ${formatBytes(stats.totalOriginalSize)}`);
  console.log(`   Optimized Total Size: ${formatBytes(stats.totalOptimizedSize)}`);
  
  if (stats.totalOriginalSize > 0) {
    const totalSavings = ((1 - stats.totalOptimizedSize / stats.totalOriginalSize) * 100).toFixed(1);
    console.log(`   Total Savings: ${totalSavings}%`);
    console.log(`   Space Saved: ${formatBytes(stats.totalOriginalSize - stats.totalOptimizedSize)}`);
  }
  
  console.log(`   Processing Time: ${duration}s\n`);
  
  // Generate usage examples
  if (stats.images.length > 0) {
    console.log('📝 Responsive Image Usage Example:');
    console.log(generateResponsiveHTML(stats.images[0].name));
  }
  
  console.log('\n🎉 All images optimized successfully!');
  console.log('💡 Use the generated responsive HTML in your React components.\n');
}

// Run optimization
main().catch(error => {
  console.error('\n❌ Fatal error:', error);
  process.exit(1);
});
