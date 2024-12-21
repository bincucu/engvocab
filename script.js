async function searchWord() {
    const word = document.getElementById('wordInput').value.trim().toLowerCase();
    const languagePair = document.getElementById('languagePair').value;

    if (!word) {
        alert('Please enter a word.');
        return;
    }

    document.getElementById('resultDisplay').innerText = 'Loading...';

    try {
        const response = await fetch(`/translate?word=${word}&langpair=${languagePair}`);
        const data = await response.json();
        if (data.error) {
            document.getElementById('resultDisplay').innerText = `Error: ${data.error}`;
        } else {
            document.getElementById('resultDisplay').innerHTML = `
                <pre><b>Word:</b> ${data.word}\n
                <b>Definitions:</b> ${data.definitions || 'No definitions found.'}\n
                <b>Examples:</b> ${data.examples || 'No examples found.'}\n
                <b>Translation:</b> ${data.translation}</pre>
            `;
        }
    } catch (error) {
        document.getElementById('resultDisplay').innerText = `Error: ${error.message}`;
    }
}
