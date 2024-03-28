const { Telegraf } = require('telegraf');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const ffmpeg = require('fluent-ffmpeg');

const bot = new Telegraf('6806028440:AAG_xNXCcfLuHAgGNZ_dn7PfJ3bHukjxd3Y');

bot.start((ctx) => {
    ctx.reply('Welcome to the Video Watermark Bot! Send me a video file to watermark it with @oremium.');
});

bot.on('video', async (ctx) => {
    const video = ctx.message.video;
    const videoSizeMB = Math.ceil(video.file_size / (1024 * 1024)); // Convert bytes to MB

    // Check if the video size is below a certain threshold before watermarking
    const MAX_VIDEO_SIZE_MB = 50; // Set your desired threshold (e.g., 50 MB)
    if (videoSizeMB > MAX_VIDEO_SIZE_MB) {
        ctx.reply(`Sorry, the video size exceeds the maximum allowed limit (${MAX_VIDEO_SIZE_MB} MB). Please send a smaller video.`);
        return;
    }

    // Create a downloads folder if it doesn't exist
    const downloadsFolderPath = './downloads';
    if (!fs.existsSync(downloadsFolderPath)) {
        fs.mkdirSync(downloadsFolderPath);
    }

    // Download video
    const videoPath = path.join(downloadsFolderPath, `${video.file_id}.mp4`);
    const writer = fs.createWriteStream(videoPath);

    const response = await axios({
        url: `https://api.telegram.org/file/bot${process.env.BOT_TOKEN}/${video.file_path}`,
        method: 'GET',
        responseType: 'stream'
    });

    response.data.pipe(writer);

    await new Promise((resolve, reject) => {
        writer.on('finish', resolve);
        writer.on('error', reject);
    });

    // Watermark video
    const watermarkedVideoPath = path.join(downloadsFolderPath, `${video.file_id}_watermarked.mp4`);
    const watermarkText = '@oremium';
    await watermarkVideo(videoPath, watermarkedVideoPath, watermarkText, ctx);

    // Send watermarked video
    await ctx.replyWithVideo({ source: watermarkedVideoPath });

    // Delete downloaded files
    fs.unlinkSync(videoPath);
    fs.unlinkSync(watermarkedVideoPath);
});

async function watermarkVideo(inputPath, outputPath, text, ctx) {
    return new Promise((resolve, reject) => {
        const command = ffmpeg(inputPath)
            .videoFilters(`drawtext=text='${text}':x=(w-text_w)/2:y=h-th-10:fontsize=24:fontcolor=white`)
            .output(outputPath)
            .on('start', (commandLine) => {
                console.log('FFmpeg command: ', commandLine);
                ctx.reply('Watermarking video. This might take a while...');
            })
            .on('progress', (progress) => {
                console.log('Processing: ' + progress.percent + '% done');
                ctx.reply(`Processing: ${progress.percent.toFixed(2)}% done`);
            })
            .on('error', (err) => {
                console.error('Error during processing', err);
                ctx.reply('Error during processing: ' + err.message);
                reject(err);
            })
            .on('end', () => {
                console.log('Processing finished successfully');
                ctx.reply('Watermarking finished successfully!');
                resolve();
            });

        command.run();
    });
}

bot.launch();
