import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList


class summarize:
    def __init__(self,model_dir=None):
        """Args:
            model_dir (str, optional): Path to the directory containing the pre-trained model. Defaults to None.
        
        Returns:
            None. Initializes the AutoTokenizer and AutoModelForCausalLM objects.
        
        Raises:
            FileNotFoundError: If the model directory does not exist.
        
        Notes:
            If the pad_token is not explicitly set in the tokenizer, it will be set to the end-of-sentence token.
            The model will be moved to the CUDA device if available.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForCausalLM.from_pretrained(model_dir, trust_remote_code=True,  torch_dtype="auto",)
        self.model.cuda()
                # Explicitly set pad_token_id if it's None
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.tokenizer.eos_token_id

    def generate(self, code, attempts=3):
        """Args:
            code (str): The code of the function you want to document.
            attempts (int, optional): The number of attempts to generate a docstring. Default is 3.
        
        Returns:
            str: A valid docstring for the given function.
        
        Raises:
            None
        
        Notes:
            This function uses a language model to generate a docstring based on a given code snippet. It attempts to generate a docstring multiple times,
            and returns the first valid one it generates.
        """
        # Required sections
        required_sections = ["Args:", "Returns:", "Raises:", "Notes:"]

        # Prepare the prompt
        prompt = f"Write a google style docstring for this python function. \
Include information about what each variable in the function input does, and if it's used or optional and what its default is if it has one.  \
do not output code.\n \
Do not write the function out. only the docstring \n\
do not add docstring quotes.\n\
do not explain about helper methods\n\
do not explain the code. docstrings explain what a function does.\n\
use this format\
---\n\
Args:\
Returns:\
Raises:\
Notes:\
---\n\
{code}\n\
# END of code\n\
# Begin your answer\n"
        for _ in range(attempts):
            inputs = self.tokenizer(prompt, return_token_type_ids=False, return_tensors="pt").to("cuda")
            tokens = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.3,
                do_sample=True,
            )
            generated_text = self.tokenizer.decode(tokens[0], skip_special_tokens=True)
            output_text = generated_text[len(self.tokenizer.decode(inputs['input_ids'][0])):]

            if all(section in output_text for section in required_sections):
                
                output_text=output_text.replace('\"\"\"','')
                output_text=output_text.replace("\'\'\'",'')
                output_text="""""+output_text+"""""
                return output_text

        return None

