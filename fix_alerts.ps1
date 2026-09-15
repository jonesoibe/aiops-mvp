# Script to replace all alert() calls with proper notifications
$files = @(
    "C:\Users\FAVOUR\aiops-mvp\templates\nexus\problems.html",
    "C:\Users\FAVOUR\aiops-mvp\templates\nexus\audit.html",
    "C:\Users\FAVOUR\aiops-mvp\templates\nexus\remediation.html",
    "C:\Users\FAVOUR\aiops-mvp\templates\outputs.html"
)

$notificationScript = @'
<script>
function showNotification(msg) {
    const notif = document.createElement('div');
    notif.style.cssText = 'position: fixed; top: 20px; right: 20px; padding: 15px 25px; background: #22c55e; color: white; border-radius: 6px; z-index: 9999; font-weight: 600;';
    notif.textContent = msg;
    document.body.appendChild(notif);
    setTimeout(() => notif.remove(), 3000);
}
</script>
'@

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Processing: $(Split-Path -Leaf $file)"
        $content = Get-Content $file -Raw
        
        # Replace alert() with showNotification()
        $content = $content -replace "alert\('([^']+)'\)", "showNotification('`$1')"
        
        # Add script if not exists
        if ($content -notmatch 'function showNotification') {
            $content = $content -replace '</body>', "$notificationScript`n</body>"
        }
        
        Set-Content $file $content
        Write-Host "✓ Fixed"
    }
}
Write-Host "All files processed!"
