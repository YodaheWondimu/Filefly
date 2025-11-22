// Function to refresh the Filefly daemon status
async function refreshStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();

        // Update dashboard elements
        document.getElementById('moved-files').textContent = data.moved_files;
        document.getElementById('watched-folders').textContent =
            data.watched_folders.join(', ');
        document.getElementById('status-active').textContent =
            data.active ? "Active" : "Inactive";
    } catch (error) {
        console.error("Error fetching status:", error);
    }
}

// Initial refresh
refreshStatus();

// Refresh every 5 seconds
setInterval(refreshStatus, 5000);