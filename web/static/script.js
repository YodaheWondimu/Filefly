async function updateStatus() {
    const res = await fetch("/status");
    const data = await res.json();
    document.getElementById("moved-files").textContent = data.moved_files;
    document.getElementById("watched-folders").textContent = data.watched_folders.join(", ");
}

setInterval(updateStatus, 3000);
updateStatus();