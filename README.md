# AmdQuant — Complex Problem Resolution

**An interactive optimization workbench powered by AMD GPUs. Define a problem, run two optimization engines, and compare both execution time and solution quality.**

[Open the web demo](https://amdquant.onrender.com/) · Prepared for [AMD Developer Hackathon: ACT III](https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-iii/)

Application version: **10.0.0**. Documentation and radio catalogue updated: **17 October 2026**. The v10 worker protocol is unchanged.

## What it does

AmdQuant turns structured optimization problems into concrete decisions: which radio channel a transmitter should use, which team receives a task, which projects to select, or where to place a computing job. Users can choose from **18 reproducible examples across five categories**, enter supported data through guided JSON templates, or define a custom quadratic binary objective.

Each problem is evaluated by two real numerical engines:

| Label in the interface | Engine | Execution |
| --- | --- | --- |
| Traditional AI micro | Classical simulated annealing, using D-Wave's compiled CPU sampler | CPU in the notebook environment |
| AI ADM Quantum micro | Simulated Bifurcation, using the open-source Python package and PyTorch | AMD GPU through ROCm |

The labels are product names. This version is a specialized optimization application: neither card is a language model. Simulated Bifurcation is a quantum-inspired algorithm running on conventional GPU hardware.

The contribution is the integrated application: problem models, guided inputs, validation, AMD execution, independently delivered results, and downloadable evidence. The underlying optimization algorithms are credited below.

## Explore the demo

1. Open the application. **Radio channels · Problem 1** is selected initially. If the GPU is offline, **Connecting…** and a spinning indicator remain visible; **Run** becomes available when the worker connects.
2. Select a category and a **Problem** button. Its description appears in the input area.
3. Press **Run**. Each result card updates when its own set of runs finishes; the faster engine does not wait for the other one.
4. Compare the objective value, reported feasibility and measured execution time.
5. Download either solution or the combined measurement. Radio problems also provide a channel-plan CSV.

The current **Problem 1** is the former **Problem 4**: 2,048 transmitters, seed `20261017`. The former 512-transmitter Problem 1 has moved to Problem 4. The two cases have exchanged places; their mathematical inputs and solver settings have not changed.

The desktop interface places problem inputs on the left and both result cards on the right. English, Spanish, French and German are available.

## Five problem categories

| Category | Built-in large examples | Guided own-data template |
| --- | --- | --- |
| **Radio channels** | Assign two channels to 512, 1,024 or 2,048 transmitters, minimizing interference between pairs using the same channel. Six examples. | Symmetric interference matrix for 2–128 transmitters. |
| **Balance tasks** | Split 2,048–4,096 tasks between two teams, accounting for both workload imbalance and competition for shared resources. Three examples. | Balance the total durations of 2–128 tasks between two equivalent teams. |
| **Select projects** | Select among 2,048–4,096 projects with individual benefits, overlap costs and collaboration gains. Three examples. | Select compatible projects with maximum benefit; 2–128 projects and explicitly listed incompatible pairs. |
| **Assign jobs** | Place 2,048–4,096 jobs in two compute pools, accounting for execution, contention and communication costs. Three examples. | One-to-one assignment of 2–10 jobs to the same number of workers using a cost matrix. |
| **Advanced QUBO** | Optimize 2,048–4,096 binary decisions with positive and negative pairwise costs. Three examples. | A user-provided quadratic matrix for 2–128 binary variables and an optional constant offset. |

The large generated models and the smaller own-data templates are explicitly different where shown in this table. The interface explains the active model. Built-in examples use synthetic data; a seed reproduces the same instance with the packaged generator.

These models have defined scope. For example, radio allocation uses two channels without coverage or power constraints. Task balance is a cost, not an exact-equality requirement. The project-selection models do not include a budget. A custom QUBO must encode the user's intended business rules.

## Enter your own problem

Select **My problem** in a category, open **How to enter your problem**, and use **Load own-data template**. Edit the JSON and select **Check data** before running it. The application rejects unsupported text, malformed JSON, invalid dimensions and unsupported fields or values.

For example, this is a complete four-transmitter input:

```json
{
  "kind": "channels",
  "weights": [
    [0, 10, 8, 1],
    [10, 0, 1, 7],
    [8, 1, 0, 6],
    [1, 7, 6, 0]
  ]
}
```

Each row and column identifies a transmitter. Weights are nonnegative costs for sharing a channel; the diagonal must be zero and the matrix symmetric. Users enter this JSON in the web input; CSV upload is not implemented in v10.

To generate the exact current Radio Channels Problem 1:

```json
{"kind":"channels","size":2048,"seed":20261017}
```

**Generate test data** supplies the appropriate `variant`, size and seed for the other large models. Keep that variant and do not mix generated specifications with own-data arrays.

A custom QUBO is interpreted as `x.T @ Q @ x + offset`, with each `x` equal to 0 or 1. Both triangles contribute: symmetric off-diagonal entries are counted twice.

## Featured recorded result — Radio channels · Problem 1

This is the case shown in the supplied demo screenshot, previously labelled
**Problem 4** and now moved to **Problem 1**. It assigns two channels to 2,048
transmitters in a dense synthetic network generated with seed `20261017`.
There are 2,096,128 distinct transmitter pairs.

| Metric visible in the recorded demo | CPU simulated annealing | AMD GPU Simulated Bifurcation |
| --- | ---: | ---: |
| Measured engine time, three calls combined | 7.34 s | 598.5 ms |
| Best remaining interference — lower is better | 5,660,967 | 5,659,642 |
| Profile | 8 reads × 200 sweeps, one thread | 128 agents × 1,000 steps |

**The web reports a 12.27× speed advantage in this measurement.** The GPU also
returned 1,325 fewer interference-cost units, approximately 0.0234% below the
CPU result. This is a small quality improvement alongside a substantial time
reduction for these particular configurations. Neither solution is certified
as globally optimal.

The times above are rounded values transcribed from the supplied screenshot;
the interface calculates its ratio using the underlying measured values. The
full JSON export for this particular run is not included in this update.
Download a fresh measurement to inspect exact timing, hardware and assignments.
The screenshot does not establish a speed guarantee for future executions,
other models or other CPU baselines. No new GPU benchmark was run to reorder
these buttons.

## Earlier export-backed radio benchmark — Problem 3

The following is a recorded result from **Radio Channels · Problem 3**, not a guaranteed result for every run or category.

- Instance: 2,048 transmitters, two channels, seed `20261016`.
- Pairwise interference entries: 2,096,128; sum of all pair weights: 11,525,632.
- GPU: **AMD Instinct MI300X VF**, ROCm `7.14.60850`, PyTorch `2.13.0+rocm7.14.0`.
- CPU baseline: `CPU_SA_8x200`, one CPU worker, eight reads and 200 sweeps per call.
- GPU profile: `SB_GPU_128x1000`, 128 agents and 1,000 steps per call.
- Three measured calls per engine; the best objective is retained.

| Metric | CPU simulated annealing | AMD GPU Simulated Bifurcation |
| --- | ---: | ---: |
| Sum of measured time across three calls | 7,345.343 ms | 654.205 ms |
| Median measured time per call | 2,457.019 ms | 215.900 ms |
| Best remaining interference — lower is better | 5,661,783 | 5,661,766 |
| Transmitters assigned exactly once | 2,048 | 2,048 |

**The GPU configuration was 11.23× faster in measured engine time and returned a slightly lower interference cost.** The cost difference was 17 units, approximately 0.00030% of the CPU result. The global optimum for this instance is unknown.

Evidence files from this run are named `amdquant-traditional-channels-solution.json` and `amdquant-quantum-channels-solution.json`. New runs export the same kind of evidence directly from the application. The source instance is identified by this matrix SHA-256:

```text
ea18fbc82e81eb145e4b374e5da052257eb27e05e5e415cb958c0e744e9994d4
```

The hash convention is the interference matrix as little-endian float64 in row-major order. Matching only a seed is insufficient when a different generator is used.

## Measurement and verification

Both engines receive the same constructed problem and run concurrently in separate, persistent processes in the AMD notebook environment. Each performs three calls. The interface releases each engine's completed result independently; it does not force the GPU to appear first.

For the radio benchmark, reported engine time includes representation preparation, GPU transfer where applicable, optimization and the in-call objective check. Initial warm-up, shared instance generation, HTTP communication, queueing and browser rendering are outside that metric. The measurement exports include additional wall-time and readiness fields. Engine time and end-to-end waiting time are different measurements.

Returned assignments are checked and their objective values are recalculated independently. **Constraints satisfied** means the encoded constraints were met; it is not a proof of optimality. Exact reference results are calculated for supported small cases. Large examples report optimality as unknown.

This comparison measures two specific algorithm-and-hardware configurations. CPU and GPU use different search settings. It does not isolate hardware acceleration using the same algorithm, establish superiority over every CPU solver, or compare against chatbot response latency. Performance and solution quality can vary by instance and environment.

## Architecture and AMD integration

The browser sends a validated job to a lightweight FastAPI gateway on Render. An authenticated worker in the AMD notebook polls the gateway over outbound HTTPS, runs both engines and publishes each completed result. The browser retrieves those results and creates the downloads.

Render hosts the interface and transient queue; it does not execute Simulated Bifurcation. The optimization dynamics, GPU candidate selection and GPU objective computation run through PyTorch on AMD ROCm. Problem construction, orchestration, the CPU baseline and independent verification also use the host CPU.

The worker verifies ROCm, GPU availability and actual GPU operations before advertising readiness. There is no CPU fallback for the GPU engine. PyTorch's `cuda:0` device name is also used by its ROCm backend and does not imply NVIDIA hardware.

## Run the application

### Render gateway

Use Python 3.12 and the project source files. The supplied `render.yaml` contains the service configuration.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn server.main:app --host 0.0.0.0 --port $PORT --workers 1
```

| Variable | Purpose |
| --- | --- |
| `GPU_WORKER_TOKEN` | Shared secret of at least 32 characters. The gateway and notebook worker must use the same value. |
| `PUBLIC_DEMO` | Set to `1` for the public browser demonstration. |
| `APP_TOKEN` | Bearer token for protected public API operations when `PUBLIC_DEMO` is `0`; the current browser interface has no login flow. |
| `PYTHON_VERSION` | The supplied Render configuration selects `3.12.14`. |

The Blueprint generates the two secrets on initial deployment. Keep them out of source control. Reuse the existing worker token when restarting a notebook. Run one gateway instance with one Uvicorn worker because the queue is held in memory.

`/healthz` checks the web service. `/api/public/info` reports worker readiness and hardware; a healthy web service alone does not mean the GPU worker is connected.

### AMD notebook — packaged setup

Use an AMD GPU notebook with a compatible ROCm-enabled PyTorch installation.

1. Upload the matching **`AmdQuant_GPU_AMD_v10.zip`**, still compressed, and **`INICIAR_AMDQUANT_V10.ipynb`** into the same Jupyter folder. These are separate release artifacts; the minimal application ZIP does not include the notebook.
2. Open the notebook and run all cells. It checks the GPU, verifies the release ZIP and prepares the worker environment while preserving the existing ROCm PyTorch build.
3. Enter the gateway's HTTPS root URL and its existing `GPU_WORKER_TOKEN` when prompted.
4. Keep the final worker cell running. Refresh the website and check GPU readiness.

The notebook verifies the exact release ZIP checksum. Adding this README or presentation files to that ZIP would change it: publish documentation alongside the unchanged release archive. The current web-only catalogue and UI update also keeps compatibility with that original worker.

### AMD notebook — source setup

For a checkout rather than the packaged release, run the following from the source root inside an AMD notebook whose `python3` already has working ROCm PyTorch:

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -c 'import torch; assert torch.version.hip and torch.cuda.is_available(); print(torch.cuda.get_device_name(0))'
python -c 'from importlib.metadata import version; print("torch==" + version("torch"))' > torch-constraint.txt
python -m pip install -c torch-constraint.txt -r requirements-gpu.txt
read -r -p 'Gateway HTTPS URL: ' RENDER_URL
export RENDER_URL
read -r -s -p 'Existing GPU_WORKER_TOKEN: ' GPU_WORKER_TOKEN
export GPU_WORKER_TOKEN
python -m server.runner
```

`requirements-gpu.txt` installs the optimization dependencies; it does not provision the AMD driver or the ROCm PyTorch build. An environment without working AMD GPU support fails the startup check.

### Reconnect after an expired session

If the existing notebook session is still available, rerun its worker cell using the same URL and token. If the provider has discarded the session, request a new AMD GPU notebook and repeat the packaged setup. The web deployment can remain in place.

The demo requires a running notebook worker. Jobs are transient, recent jobs are bounded in memory, and a gateway restart clears them. Download results that need to be retained.

### Connecting indicator and owner email alerts

When the GPU is unavailable, the browser displays **Connecting…** with a spinning
indicator and disables Run. The accompanying text explains that an administrator
must activate the GPU. The indicator has no percentage and does not claim that
a GPU is being provisioned automatically.

The page reports that a visitor is waiting. After an initial 20-second grace
period, the server requests an owner email if the GPU is still offline, then
repeats the request every **30 seconds** while visitors keep waiting. All visitors
share one timer. Alerts stop when the worker reconnects; they also stop after
60 seconds without a browser waiting signal. An email already in transit may
still arrive after reconnection. The browser refreshes readiness every 15 seconds.

Use Resend's HTTPS API. No SMTP setup is required:

| Variable | Value or purpose |
| --- | --- |
| `RESEND_API_KEY` | Your private Resend API key; store it in Render Environment. |
| `GPU_ALERT_TO` | The inbox receiving the alerts. With the default test sender, use the email associated with your Resend account. |
| `GPU_ALERT_FROM` | `AmdQuant <onboarding@resend.dev>`; this is also the default if the variable is absent. |
| `GPU_ALERT_SITE_URL` | Public HTTPS application URL; defaults to `https://amdquant.onrender.com`. |

**Do not put your Gmail address in `GPU_ALERT_FROM`.** That is the sender, not
the recipient. A custom sender requires a domain verified in Resend. A Gmail
recipient belongs in `GPU_ALERT_TO`. Registering with a Gmail account does not
authorize Resend to send as that Gmail address. See the [Resend sender-domain
requirements](https://resend.com/docs/api-reference/errors) and [test-domain
restriction](https://resend.com/docs/knowledge-base/403-error-resend-dev-domain).

At the time of this update, [Resend Free](https://resend.com/pricing) includes
100 emails per day and 3,000 per month. Sending every 30 seconds would use 100
emails in approximately 50 minutes of accumulated waiting. Quota exhaustion or
provider rejection prevents further delivery; acceptance by the API does not
prove inbox delivery. The application does not upgrade the plan or purchase
credits. Rendering the waiting indicator continues even if email delivery fails.

This is a manually reactivated experimental GPU service, not an unattended
24/7 endpoint. It does not use an AMD session cookie to promise automatic
provisioning. [Render Free](https://render.com/docs/free) may also take time to
wake up before the application can respond.

### Apply this update yourself

Replace the files in your existing web project with this package, preserving
your Render environment variables and `GPU_WORKER_TOKEN`, then deploy your
revision when you choose. The package does not perform an upload or deployment.

Keep the **original notebook v10 and its original GPU ZIP** in Jupyter. The
updated gateway forwards a validated JSON problem specification to the worker;
it does not require the notebook's old catalogue to recognize the new button
labels. The problem text displayed to the user is preserved in the gateway's
job record. This keeps the renamed examples compatible with the original v10
worker without rebuilding the GPU environment.

The files changed for the example swap are `optimizer/catalog.py`, `dist/app.js`,
`dist/index.html` and `server/gateway.py`. The README and demo narration are
updated alongside them. The existing Connecting indicator and 30-second email
behavior are retained.


## Main source areas

| Path | Responsibility |
| --- | --- |
| `dist/` | Browser interface, language strings, styles and downloads |
| `server/gateway.py` | FastAPI service, input validation, worker authentication and job queue |
| `server/alerts.py` | Owner email reminders while visitors wait for a disconnected GPU |
| `server/runner.py` | Notebook worker and outbound connection to the gateway |
| `server/protocol.py` | Shared protocol and result validation |
| `optimizer/catalog.py` | Five categories, 18 examples and guided templates |
| `optimizer/specs.py` | Supported input schemas and validation |
| `optimizer/problems.py`, `optimizer/large_problems.py` | Problem construction, decoding and verification |
| `optimizer/engines.py`, `optimizer/channel_engines.py`, `optimizer/dense_engines.py` | CPU and AMD GPU computation paths |
| `optimizer/live.py` | Concurrent solver processes and independent result delivery |

## Credits and license

- [Simulated Bifurcation Python package](https://github.com/bqth29/simulated-bifurcation-algorithm)
- [D-Wave Ocean samplers](https://docs.dwavequantum.com/en/latest/ocean/api_ref_samplers/)
- [PyTorch](https://pytorch.org/) and [AMD ROCm](https://rocm.docs.amd.com/)
- FastAPI, NumPy and Pydantic

The application source is distributed under the MIT license in `LICENSE`. Dependencies retain their respective licenses and attribution requirements.
