document.getElementById('fetchDeviceInfo').addEventListener('click', () => fetchData('/device-info'));
document.getElementById('fetchContacts').addEventListener('click', () => fetchData('/contacts'));
document.getElementById('fetchSMS').addEventListener('click', () => fetchData('/sms'));

function fetchData(endpoint) {
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            const displayDiv = document.getElementById('dataDisplay');
            displayDiv.innerHTML = ''; // Clear previous data

            if (Array.isArray(data)) {
                data.forEach(item => {
                    const p = document.createElement('p');
                    p.textContent = JSON.stringify(item);
                    displayDiv.appendChild(p);
                });
            } else {
                const p = document.createElement('p');
                p.textContent = JSON.stringify(data);
                displayDiv.appendChild(p);
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            alert('Failed to fetch data. Check the console for details.');
        });
}