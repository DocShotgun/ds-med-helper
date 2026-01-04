"""LLM (Text Generation) Functions"""

import asyncio
import json

import aiohttp
import streamlit as st

# OpenAI-compatible endpoint paths
LLM_PATH = "/v1/chat/completions"


def run_async(coro):
    """Run async coroutine in Streamlit and return result"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop and loop.is_running():
        # Already in async context, need to await the task
        async def await_task():
            return await coro
        
        # Create a new event loop for this task
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(await_task())
        finally:
            new_loop.close()
    else:
        # Synchronous context - use asyncio.run
        return asyncio.run(coro)


async def llm_stream_to_list(
    prompt: str,
    system_prompt: str,
    endpoint: str,
    model: str,
    max_tokens: int = -1,
    temperature: float = 0.8,
    top_k: int = 40,
    top_p: float = 0.95,
    min_p: float = 0.05
) -> list:
    """
    Generic LLM streaming completion - collects all chunks into a list.
    
    Per OpenAI API spec (POST /chat/completions with stream=True):
    - Set stream=True in request body
    - Server sends Server-Sent Events (SSE) format
    - Each event contains delta content
    
    Args:
        prompt: User prompt
        system_prompt: System instruction
        endpoint: Base LLM endpoint URL (e.g., http://localhost:8080)
        model: Model name
        max_tokens: Max tokens to generate (-1 for unlimited)
        temperature: Sampling temperature
        top_k: Top-k sampling parameter
        top_p: Top-p sampling parameter
        min_p: Minimum probability sampling parameter
    
    Returns:
        List of text chunks from the stream
    """
    # Append OpenAI-compatible path
    full_endpoint = f"{endpoint.rstrip('/')}{LLM_PATH}"
    
    chunks = []
    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "min_p": min_p,
            "stream": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                full_endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as resp:
                if resp.status == 200:
                    async for line in resp.content:
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith(b'data: '):
                            data = line[6:]
                            if data == b'[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                if chunk.get('choices'):
                                    delta = chunk['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        chunks.append(content)
                            except json.JSONDecodeError:
                                continue
                else:
                    error_text = await resp.text()
                    st.error(f"LLM Streaming Error: {resp.status} - {error_text}")
    except Exception as e:
        st.error(f"LLM Streaming Error: {e}")
    
    return chunks
