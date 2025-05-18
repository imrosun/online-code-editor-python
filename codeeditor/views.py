import sys
import io
import json
import builtins
import traceback
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
            return JsonResponse({'status': 'error', 'output': 'Invalid JSON', 'is_error': True})

        code = data.get('code', '')
        inputs = data.get('inputs', [])
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

        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        old_input = builtins.input
        builtins.input = input_patch

        try:
            try:
                compiled_code = compile(code, 'main.py', 'exec')
                exec(compiled_code, {})
            except EOFError as e:
                sys.stdout = old_stdout
                builtins.input = old_input
                output = mystdout.getvalue()
                new_output = output[last_output_len:]
                return JsonResponse({
                    'status': 'input',
                    'prompt': str(e),
                    'output': new_output,
                    'last_output_len': len(output),
                    'is_error': False
                })
            except Exception as exc:
                sys.stdout = old_stdout
                builtins.input = old_input
                tb_exc = traceback.TracebackException.from_exception(exc)
                tb_lines = list(tb_exc.format())
                # Find the first line with 'File "main.py"'
                for i, line in enumerate(tb_lines):
                    if 'File "main.py"' in line:
                        # Always include the "Traceback (most recent call last):" header
                        tb_filtered = tb_lines[0:1] + tb_lines[i:]
                        break
                else:
                    # Fallback: show the whole traceback
                    tb_filtered = tb_lines
                tb_str = ''.join(tb_filtered)
                output = mystdout.getvalue() + tb_str
                new_output = output[last_output_len:]
                return JsonResponse({'status': 'done', 'output': new_output, 'is_error': True})

            sys.stdout = old_stdout
            builtins.input = old_input
            output = mystdout.getvalue()
            new_output = output[last_output_len:]
            return JsonResponse({'status': 'done', 'output': new_output, 'is_error': False})

        except Exception as e:
            sys.stdout = old_stdout
            builtins.input = old_input
            tb_exc = traceback.TracebackException.from_exception(e)
            tb_str = ''.join(tb_exc.format())
            return JsonResponse({'status': 'done', 'output': tb_str, 'is_error': True})

    return JsonResponse({'status': 'error', 'output': 'Invalid request', 'is_error': True})
