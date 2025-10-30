import { pipeline, env } from "@huggingface/transformers";

// Skip local model check
env.allowLocalModels = false;

// Singleton for the translation pipeline
class PipelineSingleton {
  static task = 'translation';
  static model = 'Xenova/nllb-200-distilled-600M';
  static instance = null;

  static async getInstance(progress_callback = null) {
    if (this.instance === null) {
      this.instance = pipeline(this.task, this.model, { progress_callback });
    }
    return this.instance;
  }
}

// Listen for messages
self.addEventListener('message', async (event) => {
  // Load the pipeline
  let translator = await PipelineSingleton.getInstance(x => {
    self.postMessage(x);
  });

  // Perform translation
  let output = await translator(event.data.text, {
    src_lang: event.data.src_lang,
    tgt_lang: event.data.tgt_lang,
  });

  // Send result back
  self.postMessage({
    status: 'complete',
    output: output,
  });
});