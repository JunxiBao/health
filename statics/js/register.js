const loadingOverlay = document.createElement('div');
loadingOverlay.id = 'loading-overlay';
loadingOverlay.innerHTML = '<div class="spinner"></div>';
document.body.appendChild(loadingOverlay);

const style = document.createElement('style');
style.innerHTML = `
#loading-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(255, 255, 255, 0.8);
  z-index: 9999;
  display: none;
  align-items: center;
  justify-content: center;
  transition: background 0.3s ease;
}

@media (prefers-color-scheme: dark) {
  #loading-overlay {
    background: rgba(0, 0, 0, 0.6);
  }

  .spinner {
    border: 6px solid #444;
    border-top-color: #b197fc;
  }
}

.spinner {
  width: 50px;
  height: 50px;
  border: 6px solid #ccc;
  border-top-color: #7b2cbf;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
`;
document.head.appendChild(style);

const popup = document.getElementById("popup");
const popupText = document.getElementById("popupText");

function showPopup(message, time = 2000) {
  popupText.textContent = message;
  popup.classList.add("show");
  setTimeout(() => {
    popup.classList.remove("show");
  }, time);
}

document.getElementById('registerBtn').addEventListener('click', function () {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  const age = document.getElementById('age').value.trim();

  if (!username) {
    showPopup('用户名不能为空');
    return;
  }

  if (username.length > 20) {
    showPopup('用户名不能超过20个字符');
    return;
  }

  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,20}$/;
  if (!passwordRegex.test(password)) {
    showPopup('密码必须为8到20位，包含大写字母、小写字母和数字');
    return;
  }

  if (password !== confirmPassword) {
    showPopup('两次输入的密码不一致');
    return;
  }

  // 年龄校验：必须是1-120的整数
  const ageNum = Number(age);
  if (!age || isNaN(ageNum) || !Number.isInteger(ageNum) || ageNum < 1 || ageNum > 120) {
    showPopup('年龄必须是1-120之间的整数');
    return;
  }

  showLoading();
  fetch('https://zhucan.xyz:5000/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password, age })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      showPopup('注册成功！');
      setTimeout(() => {
        window.location.href = 'login.html';
        hideLoading();
      }, 1500);
    } else {
      showPopup('注册失败: ' + data.message);
      hideLoading();
    }
  })
  .catch(error => {
    showPopup('网络错误: ' + error);
    hideLoading();
  });
});

function showLoading() {
  loadingOverlay.style.display = 'flex';
}

function hideLoading() {
  loadingOverlay.style.display = 'none';
}

// 初始化隐藏
hideLoading();