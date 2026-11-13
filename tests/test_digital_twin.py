
import simpy

from src.digital_twin.simulation import InventorySimulation


def create_simulation(
    initial_stock=100,
    daily_demand=25,
    reorder_point=40,
    reorder_quantity=150,
    lead_time=3,
):
    env = simpy.Environment()

    simulation = InventorySimulation(
        env=env,
        initial_stock=initial_stock,
        daily_demand=daily_demand,
        reorder_point=reorder_point,
        reorder_quantity=reorder_quantity,
        lead_time=lead_time,
    )

    env.process(simulation.consume_inventory())

    return env, simulation


def test_inventory_consumption():
    env, simulation = create_simulation()

    env.run(until=2)

    assert simulation.stock == 50
    assert simulation.total_demand == 50
    assert simulation.total_fulfilled == 50


def test_replenishment():
    env, simulation = create_simulation()

    env.run(until=6)

    assert simulation.stock == 125
    assert simulation.pending_order is False


def test_stockout_detection():
    env, simulation = create_simulation()

    env.run(until=5)

    assert simulation.total_stockouts == 1
    assert simulation.total_fulfilled == 100


def test_full_simulation():
    env, simulation = create_simulation()

    env.run(until=15)

    assert simulation.total_demand == 375
    assert simulation.total_fulfilled == 325
    assert simulation.total_stockouts == 2
    assert simulation.stock == 75


def test_no_stockout_with_sufficient_inventory():
    env, simulation = create_simulation(
        initial_stock=500,
        daily_demand=10,
        reorder_point=40,
        reorder_quantity=150,
        lead_time=3,
    )

    env.run(until=10)

    assert simulation.total_stockouts == 0
    assert simulation.stock == 400
