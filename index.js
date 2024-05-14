const express = require('express');
const axios = require('axios');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
    const videoUrl = req.query.url;
    if (!videoUrl) {
        return res.status(400).send('Please provide a video URL using the "url" query parameter.');
    }

    downloadVideo(videoUrl)
        .then((downloadId) => {
            res.send(`/downloads/${downloadId}.mp4`);
        })
        .catch((error) => {
            console.error('Error occurred during download:', error);
            res.status(500).send('Failed to download video');
        });
});

async function downloadVideo(videoUrl) {
    const downloadId = uuidv4();
    const response = await axios({
        url: videoUrl,
        method: 'GET',
        responseType: 'stream'
    });

    const filePath = `./downloads/${downloadId}.mp4`;
    const writer = fs.createWriteStream(filePath);
    response.data.pipe(writer);

    await new Promise((resolve, reject) => {
        response.data.on('end', resolve);
        response.data.on('error', reject);
    });

    return downloadId;
}

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
