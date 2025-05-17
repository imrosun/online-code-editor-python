import sys
import io
import json
import builtins
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

PYTHON_VERSION = sys.version.split()[0]

def index(request):
    return render(request, 'index.html', {'python_version': PYTHON_VERSION})

@csrf_exempt
def runcode(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'status': 'error', 'output': 'Invalid JSON'})

        code = data.get('code', '')
        inputs = data.get('inputs', [ ])
        last_output_len = data.get('last_output_len', 0)

        input_counter = 0

        def input_patch(prompt=' '):
            nonlocal input_counter
            if input_counter < len(inputs):
                val = inputs[input_counter]
                input_counter += 1
                return val
            else:
                raise EOFError(prompt)

        try:
            old_stdout = sys.stdout
            sys.stdout = mystdout = io.StringIO()
            old_input = builtins.input
            builtins.input = input_patch

            try:
                exec(code, {})
            except EOFError as e:
                sys.stdout = old_stdout
                builtins.input = old_input
                output = mystdout.getvalue()
                # Only return new output since last input
                new_output = output[last_output_len:]
                return JsonResponse({
                    'status': 'input',
                    'prompt': str(e),
                    'output': new_output,
                    'last_output_len': len(output)
                })

            sys.stdout = old_stdout
            builtins.input = old_input
            output = mystdout.getvalue()
            new_output = output[last_output_len:]
            return JsonResponse({'status': 'done', 'output': new_output})

        except Exception as e:
            sys.stdout = old_stdout
            builtins.input = old_input
            return JsonResponse({'status': 'done', 'output': str(e)})

    return JsonResponse({'status': 'error', 'output': 'Invalid request'})
