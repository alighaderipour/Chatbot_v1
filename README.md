https://github.com/ggml-org/llama.cpp/releases/download/b10158/llama-b10158-bin-win-cuda-12.4-x64.zip
https://github.com/ggml-org/llama.cpp/releases/download/b10158/cudart-llama-bin-win-cuda-12.4-x64.zip


in llama.cpp-cuda12 folder
.\llama-server.exe -m "C:\Projects\Chatbot_v1\models\Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q8_K_P.gguf" --host 127.0.0.1 --port 8080 -c 65536 -ngl 999 --flash-attn on --cache-type-k q8_0 --cache-type-v q8_0 --parallel 8 




"C:\Projects\Chatbot_v1\models\Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q8_K_P.gguf"
put model in models folder



pnpm run dev -- --host 0.0.0.0       

python serve.py