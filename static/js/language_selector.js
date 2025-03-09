// 语言选择器功能
document.addEventListener('DOMContentLoaded', function() {
    // 获取语言选择器
    const languageSelector = document.getElementById('language-selector');
    if (languageSelector) {
        languageSelector.addEventListener('change', function() {
            // 获取当前URL
            const url = new URL(window.location.href);
            // 设置lang参数
            url.searchParams.set('lang', this.value);
            // 跳转到新URL
            window.location.href = url.toString();
        });
    }
}); 