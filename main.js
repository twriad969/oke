const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram bot token
const bot = new TelegramBot('6663409312:AAHcW5A_mnhWHwSdZrFm9eJx1RxqzWKrS0c', { polling: true });

// Create the downloads folder if it doesn't exist
const downloadsFolder = path.join(__dirname, 'downloads');
if (!fs.existsSync(downloadsFolder)) {
    fs.mkdirSync(downloadsFolder);
}

// Function to download video from Terabox link
async function downloadVideo(url, chatId) {
    try {
        const response = await axios.get(`https://ronokkingapis.ronok.workers.dev/?link=${encodeURIComponent(url)}`);
        console.log('API Response:', response.data);

        // Parse JSON response and extract download link
        const responseData = response.data;
        let downloadLink = responseData.downloadLink;

        // Modify Terabox domain in download link
        downloadLink = downloadLink.replace('https://d-jp01-ntt.terabox.com', 'https://d3.terabox.app');

        // Download the video
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
                bot.sendMessage(chatId, `Downloading: ${progress.toFixed(2)}%`);
                lastSentProgress = progress;
            }
        });

        // Once download is complete, send the video to the user
        writer.on('finish', () => {
            bot.sendVideo(chatId, fs.createReadStream(filePath));
        });
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Listen for messages
bot.on('message', (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text;

    if (text && text.startsWith('https://teraboxapp.com')) {
        bot.sendMessage(chatId, '📥 Downloading video...');

        // Start downloading the video
        downloadVideo(text, chatId);
    } else {
        bot.sendMessage(chatId, '❌ Please send a valid Terabox video link.');
    }
});

// Start message
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, `
👋 Hello! I'm the Terabox Video Downloader Bot.

To download a video from Terabox, simply send me the Terabox video link and I'll take care of the rest.

Example: https://teraboxapp.com/your-video-link

Let's get started!`);
});
