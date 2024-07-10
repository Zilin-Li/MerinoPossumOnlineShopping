document.querySelectorAll('.amount-btn').forEach(button => {
    button.addEventListener('click', function() {
        document.querySelectorAll('.amount-btn').forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
        document.getElementById('selectedValue').value = this.getAttribute('data-value');
    });
});

document.querySelectorAll('.collapsible-header').forEach(header => {
    header.addEventListener('click', function() {
        const content = this.nextElementSibling;
        const arrow = this.querySelector('.collapsible-arrow');
        
        // 切换内容的显示状态
        content.classList.toggle('show');
        
        // 切换箭头方向和标题的活动状态
        this.classList.toggle('active');
    });
});