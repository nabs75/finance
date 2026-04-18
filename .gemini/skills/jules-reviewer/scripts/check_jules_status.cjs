const { execSync } = require('child_process');

function checkJulesStatus() {
  try {
    const version = execSync('jules --version', { encoding: 'utf8' }).trim();
    console.log(`Jules CLI found: ${version}`);
    
    try {
      // Trying a command that requires login to check auth status
      // 'jules remote list --repo' usually checks auth
      execSync('jules remote list --repo', { encoding: 'utf8', stdio: 'ignore' });
      console.log('Status: Logged in and ready.');
    } catch (e) {
      console.log('Status: Not logged in. Run "jules login" to authenticate.');
    }
  } catch (e) {
    console.error('Error: Jules CLI not found. Install it with "npm install -g @google/jules".');
    process.exit(1);
  }
}

checkJulesStatus();
