export function getFileIcon(fileUrl: string):string {
    const extension = fileUrl.split('.').pop()?.toLowerCase();
    switch (extension) {
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
        case 'webp':
            return '🖼️'; // Image icon
        case 'txt':
            return '📄'; // Text file
        case 'doc':
        case 'docx':
            return '📝'; // Word document
        case 'md':
            return '📖'; // Markdown
        case 'xlsx':
        case 'csv':
            return '📊'; // Spreadsheet
        case 'pdf':
            return '📑'; // PDF
        default:
            return '📎'; // Generic file
    }
};