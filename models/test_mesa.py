import mesa
import time
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.progress import Progress

# --- 1. Scientific Logic (Mesa 3.5.1) ---
def compute_gini(model):
    agent_wealths = [a.wealth for a in model.agents]
    x = sorted(agent_wealths)
    N = len(agent_wealths)
    if N == 0 or sum(x) == 0: return 0
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B

class WealthAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.wealth = 1

    def step(self):
        if self.wealth > 0:
            other = self.model.random.choice(list(self.model.agents))
            if other is not self:
                other.wealth += 1
                self.wealth -= 1

class WealthModel(mesa.Model):
    def __init__(self, N):
        super().__init__()
        for _ in range(N):
            WealthAgent(self)
        self.datacollector = mesa.DataCollector(model_reporters={"Gini": compute_gini})

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

# --- 2. The "Fancy" UI Logic ---
def generate_table(step, gini, model) -> Table:
    table = Table(title=f"Mesa Simulation Step: [bold cyan]{step}[/bold cyan]")
    table.add_column("Metric", style="magenta")
    table.add_column("Value", justify="right", style="green")
    
    table.add_row("Gini Coefficient", f"{gini:.4f}")
    table.add_row("Total Agents", str(len(model.agents)))
    table.add_row("System Status", "[bold pulse green]RUNNING[/bold pulse green]")
    
    # Show top 3 wealthiest agents
    top_wealths = sorted([a.wealth for a in model.agents], reverse=True)[:3]
    table.add_row("Top Wealth Tier", str(top_wealths))
    
    return table

# --- 3. Execution with Live Animation ---
console = Console()
model = WealthModel(50)
total_steps = 30

console.print(Panel("[bold yellow]Initializing GSoC High-Performance Simulation Environment[/bold yellow]", expand=False))

with Live(generate_table(0, 0, model), refresh_per_second=4) as live:
    for i in range(1, total_steps + 1):
        model.step()
        current_gini = model.datacollector.get_model_vars_dataframe().iloc[-1]["Gini"]
        
        # Artificial delay to make the animation "feel" smooth
        time.sleep(0.2) 
        live.update(generate_table(i, current_gini, model))

console.print("\n[bold green]✔ Simulation Exported to DataCollector.[/bold green]")
console.print("[bold cyan]Ready for LLM Reasoning Layer Integration.[/bold cyan]")