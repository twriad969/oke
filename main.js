const { Telegraf } = require('telegraf');
const fs = require('fs');
const path = require('path');
const ffmpeg = require('fluent-ffmpeg');
const { exec } = require('child_process');

const bot = new Telegraf('6806028440:AAG_xNXCcfLuHAgGNZ_dn7PfJ3bHukjxd3Y');

bot.start((ctx) => ctx.reply('Welcome to the Video Watermark Bot! Send me a video file to watermark it with @oremium.'));

bot.on('video', async (ctx) => {
    const video = ctx.message.video;

    // Create downloads folder if it doesn't exist
    const downloadsFolderPath = './downloads';
    if (!fs.existsSync(downloadsFolderPath)) {
        fs.mkdirSync(downloadsFolderPath);
    }

    // Download video
    const videoPath = path.join(downloadsFolderPath, `${video.file_id}.mp4`);
    await ctx.telegram.getFile(video.file_id).then((file) => {
        ctx.telegram.downloadFile(file.file_path, videoPath);
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
            .videoFilters(`drawtext=text='${text}':x=(w-text_w)/2:y=(h-text_h)/2`)
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
