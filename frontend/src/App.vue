<template>
  <div id="app">
    <div class="container">
      <h1>Добавь смайлик в видео!</h1>

      <div class="upload-section">
        <input
          type="file"
          @change="handleFileUpload"
          accept="video/mp4,video/mov,video/avi"
          :disabled="processing"
          class="file-input"
        />
        <button
          @click="addEmoji"
          :disabled="!file || processing"
          class="btn btn-primary"
        >
          {{ processing ? 'Обработка...' : 'Добавить 😊' }}
        </button>
      </div>

      <div v-if="error" class="error-message">
        ❌ {{ error }}
      </div>

      <div v-if="processing" class="loading">
        ⏳ Обрабатываем видео...
      </div>

      <div v-if="resultUrl" class="result-section">
        <h3>✅ Готово!</h3>
        <video :src="resultUrl" controls class="video-player"></video>
        <div class="download-section">
          <a :href="resultUrl" download="video_with_emoji.mp4" class="btn btn-success">
            Скачать видео
          </a>
          <button @click="reset" class="btn btn-secondary">
            Новое видео
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      file: null,
      processing: false,
      error: null,
      resultUrl: null
    }
  },
  methods: {
    handleFileUpload(event) {
      this.file = event.target.files[0]
      this.error = null
      this.resultUrl = null

      // Валидация размера файла
      if (this.file && this.file.size > 11 * 1024 * 1024) {
        this.error = 'Файл слишком большой. Максимальный размер: 11МБ'
        this.file = null
      }
    },

    async addEmoji() {
      if (!this.file) return

      this.processing = true
      this.error = null

      const formData = new FormData()
      formData.append('file', this.file)

      try {
        const response = await fetch('/api/add-emoji', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Ошибка сервера')
        }

        const blob = await response.blob()
        this.resultUrl = URL.createObjectURL(blob)
      } catch (err) {
        this.error = err.message
      } finally {
        this.processing = false
      }
    },

    reset() {
      this.file = null
      this.resultUrl = null
      this.error = null
      // Сбрасываем input file
      const fileInput = document.querySelector('.file-input')
      if (fileInput) fileInput.value = ''
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.container {
  background: white;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  max-width: 600px;
  width: 100%;
  text-align: center;
}

h1 {
  color: #333;
  margin-bottom: 30px;
  font-size: 2em;
}

.upload-section {
  margin: 30px 0;
}

.file-input {
  display: block;
  width: 100%;
  margin: 15px 0;
  padding: 12px;
  border: 2px dashed #ccc;
  border-radius: 8px;
  background: #f9f9f9;
  cursor: pointer;
}

.file-input:hover {
  border-color: #667eea;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  margin: 5px;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5a6fd8;
}

.btn-success {
  background: #48bb78;
  color: white;
}

.btn-success:hover {
  background: #38a169;
}

.btn-secondary {
  background: #a0aec0;
  color: white;
}

.btn-secondary:hover {
  background: #718096;
}

.error-message {
  background: #fed7d7;
  color: #c53030;
  padding: 15px;
  border-radius: 8px;
  margin: 20px 0;
}

.loading {
  color: #667eea;
  font-size: 18px;
  margin: 20px 0;
}

.result-section {
  margin-top: 30px;
  animation: fadeIn 0.5s ease;
}

.video-player {
  width: 100%;
  max-width: 500px;
  border-radius: 8px;
  margin: 20px 0;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.download-section {
  margin-top: 20px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 600px) {
  .container {
    padding: 20px;
    margin: 10px;
  }

  h1 {
    font-size: 1.5em;
  }
}
</style>
