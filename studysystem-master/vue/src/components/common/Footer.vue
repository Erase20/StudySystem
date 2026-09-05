<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="footer-section">
          <h3 class="section-title">关于我们</h3>
          <p class="section-desc">在线学习平台致力于为学习者提供高质量的课程和学习资源，帮助您实现个人和职业发展目标。</p>
        </div>
        <div class="footer-section">
          <h3 class="section-title">快速链接</h3>
          <ul class="link-list">
            <li><a href="/front">首页</a></li>
            <li><a href="/front/course">课程</a></li>
            <li><a href="/front/information">资料</a></li>
            <li><a href="/front/learningCenter">学习中心</a></li>
            <li><a href="/front/dataAnalysis">数据分析</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h3 class="section-title">联系我们</h3>
          <ul class="contact-list">
            <li>邮箱：contact@learningplatform.com</li>
            <li>电话：400-123-4567</li>
            <li>地址：北京市海淀区中关村大街1号</li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p class="copyright">© 2026 在线学习平台 版权所有</p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {}
</script>

<style scoped>
.footer {
  background: #1e293b;
  color: #fff;
  padding: 48px 0 24px;
  margin-top: 48px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 48px;
  margin-bottom: 32px;
}

.footer-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #fff;
}

.section-desc {
  font-size: 14px;
  line-height: 1.6;
  color: #94a3b8;
  margin: 0;
}

.link-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.link-list li {
  margin-bottom: 12px;
}

.link-list a {
  color: #94a3b8;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s;
}

.link-list a:hover {
  color: #fff;
}

.contact-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.contact-list li {
  margin-bottom: 12px;
  font-size: 14px;
  color: #94a3b8;
}

.footer-bottom {
  border-top: 1px solid #334155;
  padding-top: 24px;
  text-align: center;
}

.copyright {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

/* 响应式 */
@media (max-width: 900px) {
  .footer-content {
    grid-template-columns: repeat(2, 1fr);
    gap: 32px;
  }
}

@media (max-width: 600px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .footer {
    padding: 32px 0 16px;
  }
  
  .footer-container {
    padding: 0 16px;
  }
}
</style>