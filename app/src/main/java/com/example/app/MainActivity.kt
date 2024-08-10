package com.example.app

import android.Manifest
import android.content.ContentValues
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.provider.MediaStore
import android.util.Log
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.google.android.material.button.MaterialButton
import okhttp3.Call
import okhttp3.Callback
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import java.io.IOException

class MainActivity : AppCompatActivity() {
    private lateinit var startButton: MaterialButton
    private lateinit var stopButton: MaterialButton
    private lateinit var saveButton: MaterialButton
    private lateinit var logsTextView: TextView
    private val client = OkHttpClient()
    private val handler = Handler(Looper.getMainLooper())
    private var stopLogcatRunnable: Runnable? = null
    private var serverAddress = BuildConfig.SERVER_ADDRESS

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        startButton = findViewById(R.id.startButton)
        stopButton = findViewById(R.id.stopButton)
        saveButton = findViewById(R.id.saveButton)
        logsTextView = findViewById(R.id.scrollableTextView)

        startButton.setOnClickListener { startLogcat() }
        stopButton.setOnClickListener { stopLogcat() }
        saveButton.setOnClickListener { saveToFile() }

        requestStoragePermissions()
    }

    private fun startLogcat() {
        val request = Request.Builder()
                .url("$serverAddress/start")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e("HttpResponse", "Request failed: ${e.message}")
                runOnUiThread { "Request failed: ${e.message}".also { logsTextView.text = it } }
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    val responseBody = response.body?.string() ?: "No response body"
                    Log.d("HttpResponse", "Response: $responseBody")
                    runOnUiThread { logsTextView.text = responseBody }

                    stopLogcatRunnable?.let {
                        handler.removeCallbacks(it)
                    }
                    stopLogcatRunnable = Runnable { stopLogcat() }
                    handler.postDelayed(stopLogcatRunnable!!, 30000) // 30 seconds
                }
            }
        })
    }

    private fun stopLogcat() {
        val request = Request.Builder()
            .url("$serverAddress/stop")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e("HttpResponse", "Request failed: ${e.message}")
                runOnUiThread { "Request failed: ${e.message}".also { logsTextView.text = it } }
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    val responseBody = response.body?.string() ?: "No response body"
                    Log.d("HttpResponse", "Response: $responseBody")
                    runOnUiThread { logsTextView.text = responseBody }
                }
            }
        })
    }

    private fun saveToFile() {
        if (isExternalStorageWritable()) {
            val contentResolver = contentResolver
            val contentValues = ContentValues().apply {
                put(MediaStore.MediaColumns.DISPLAY_NAME, "logcat_output.txt")
                put(MediaStore.MediaColumns.MIME_TYPE, "text/plain")
                put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOCUMENTS)
            }

            val uri = contentResolver.insert(MediaStore.Files.getContentUri("external"), contentValues)

            uri?.let {
                try {
                    contentResolver.openOutputStream(it).use { outputStream ->
                        outputStream?.write(logsTextView.text.toString().toByteArray())
                    }
                    Toast.makeText(this, "Saved to Documents", Toast.LENGTH_SHORT).show()
                } catch (e: IOException) {
                    e.printStackTrace()
                    Toast.makeText(this, "Error saving file", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun requestStoragePermissions() {
        val permissions = mutableListOf<String>()

        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
            permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
        }

        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, permissions.toTypedArray(), 1)
        }
    }

    private fun isExternalStorageWritable(): Boolean {
        return Environment.getExternalStorageState() == Environment.MEDIA_MOUNTED
    }
}