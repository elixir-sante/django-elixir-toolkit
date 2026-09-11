
function MyClipboardIframePlugin(editor) {
    const clipboard = editor.plugins.get('ClipboardPipeline');

    clipboard.on('inputTransformation', (evt, data) => {
        const text = data.dataTransfer.getData('text/plain') || '';
        const iframeMatch = text.match(/<iframe[\s\S]*?<\/iframe>/i);
        if (text && iframeMatch) {
            evt.stop();
            editor.execute('htmlEmbed', iframeMatch);
        }
    });

    console.log("MyClipboardIframePlugin plugin loaded.");
}

function MyClipboardBlockquotePlugin(editor) {
    const clipboard = editor.plugins.get('ClipboardPipeline');

    clipboard.on('inputTransformation', (evt, data) => {
        const text = data.dataTransfer.getData('text/plain') || '';
        const blockquoteMatch = text.match(/<blockquote[\s\S]*?<\/blockquote>\s*(?:<script[\s\S]*?<\/script>)?/i);
        if (text && blockquoteMatch) {
            evt.stop();
            editor.execute('htmlEmbed', blockquoteMatch[0]);
        }
    });

    console.log("MyClipboardBlockquotePlugin plugin loaded.");
}
