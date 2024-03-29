const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const express = require('express');

const app = express();

// Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram bot token
const bot = new TelegramBot('6663409312:AAHcW5A_mnhWHwSdZrFm9eJx1RxqzWKrS0c', { polling: true });

// Create the downloads folder if it doesn't exist
const downloadsFolder = path.join(__dirname, 'downloads');
if (!fs.existsSync(downloadsFolder)) {
    fs.mkdirSync(downloadsFolder);
}

// Function to download video from Terabox link
async function downloadVideo(url, chatId) {
    let messageId = null;

    try {
        // Send initial message
        bot.sendMessage(chatId, '🔄 Requesting API...').then((message) => {
            messageId = message.message_id;
        });

        const response = await axios.get(`https://ronokkingapis.ronok.workers.dev/?link=${encodeURIComponent(url)}`);
        console.log('API Response:', response.data);

        // Parse JSON response and extract download link
        const responseData = response.data;
        let downloadLink = responseData.downloadLink;

        // Modify Terabox domain in download link
        downloadLink = downloadLink.replace('https://d-jp01-ntt.terabox.com', 'https://d3.terabox.app');

        // Update message
        await bot.editMessageText('📥 Downloading...', { chat_id: chatId, message_id: messageId });

        // Start downloading the video
        const videoResponse = await axios({
            method: 'GET',
            url: downloadLink,
            responseType: 'stream'
        });

        const filePath = path.join(downloadsFolder, 'video.mp4');
        const writer = fs.createWriteStream(filePath);

        videoResponse.data.pipe(writer);

        // Send progress updates
        let lastSentProgress = 0;
        videoResponse.data.on('data', (chunk) => {
            const progress = (writer.bytesWritten / videoResponse.headers['content-length']) * 100;
            if (progress - lastSentProgress > 5) { // Send update only if progress increased by 5%
                bot.editMessageText(`📥 Downloading: ${progress.toFixed(2)}%`, { chat_id: chatId, message_id: messageId });
                lastSentProgress = progress;
            }
        });

        // Once download is complete, send the video to the user
        writer.on('finish', () => {
            bot.sendMessage(chatId, '⬆️ Uploading to you...').then((message) => {
                // Send the video to the user
                bot.sendVideo(chatId, fs.createReadStream(filePath)).then(() => {
                    // Delete progress message
                    bot.deleteMessage(chatId, messageId);
                });
            });
        });
    } catch (error) {
        console.error('Error:', error.message);
        if (messageId) {
            // Send error message
            bot.editMessageText('❌ An error occurred.', { chat_id: chatId, message_id: messageId });
        } else {
            bot.sendMessage(chatId, '❌ An error occurred.');
        }
    }
}

// Handle incoming HTTP requests
app.post('/download', express.json(), (req, res) => {
    const { chatId, videoUrl } = req.body;

    if (chatId && videoUrl) {
        // Start downloading the video
        downloadVideo(videoUrl, chatId);
        res.sendStatus(200);
    } else {
        res.status(400).send('Invalid request');
    }
});

// Start the Express server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

// Listen for messages
bot.on('message', (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text;

    if (text && text.startsWith('https://teraboxapp.com')) {
        bot.sendMessage(chatId, '📥 Downloading video...');

        // Send HTTP request to start downloading the video
        axios.post('https://randiwter-0457f33f461f.herokuapp.com//download', { chatId, videoUrl: text })
            .then(() => console.log('Download request sent'))
            .catch(error => console.error('Error sending download request:', error));
    }
});

// Start message
let firstTime = true;
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    if (firstTime) {
        bot.sendMessage(chatId, `
👋 Hello! I'm the Terabox Video Downloader Bot.

To download a video from Terabox, simply send me the Terabox video link and I'll take care of the rest.

Example: https://teraboxapp.com/your-video-link

Let's get started!`);
        firstTime = false;
    }
});
