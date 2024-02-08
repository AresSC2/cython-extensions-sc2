from typing import Union

from sc2.bot_ai import BotAI
from sc2.unit import Unit
from sc2.units import Units

def cy_attack_ready(ai: BotAI, unit: Unit, target: Unit) -> bool:
    """Check if the unit is ready to attack the target.

    Takes into account turn rate and unit speeds

    Example:
    ```py
    from cython_extensions import cy_attack_ready

    worker = self.workers[0]
    target = self.enemy_units[0]

    attack_ready: bool = cy_attack_ready(self, worker, target)
    ```

    ```
    1.46 µs ± 5.45 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)

    Python alternative:
    5.66 µs ± 21.2 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
    ```

    Parameters
    ----------
    ai :
        Bot object that will be running the game.
    unit :
        The unit we want to check.
    target :
        The thing we want to shoot.

    Returns
    -------
    bool :
        Is the unit ready to attack the target?

    """
    ...

def cy_is_facing(unit: Unit, other_unit: int, angle_error: float) -> bool:
    """Get turn speed of unit in radians

    Example:
    ```py
    from cython_extensions import cy_is_facing

    unit: Unit = self.workers[0]
    other_unit: Unit = self.townhalls[0]
    is_facing: bool = cy_is_facing(unit, other_unit)
    ```
    ```
    323 ns ± 3.93 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)

    Python-sc2's `unit.is_facing(other_unit)` alternative:
    2.94 µs ± 8 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
    ```

    Parameters
    ----------
    unit :
        The actual sc2.Unit object we are checking.
    other_unit :
        The unit type id integer value.
    angle_error : (default=0.3)
        Some leeway when deciding a unit is facing.

    Returns
    -------
    bool :
        Is facing the other unit?
    """
    ...

def cy_pick_enemy_target(enemies: Union[Units, list[Unit]]) -> Unit:
    """Pick the best thing to shoot at out of all enemies.

    Example:
    ```py
    from cython_extensions import cy_pick_enemy_target
    from sc2.units import Units
    from sc2.unit import Unit

    enemies: Units = self.enemy_units

    target: Unit = cy_pick_enemy_target(enemies)
    ```
    ```
    70.5 µs ± 818 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)

    Python alternative:
    115 µs ± 766 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)
    ```

    Parameters
    ----------
    enemies :
        All enemy units we would like to check.

    Returns
    -------
    Unit :
        The best unit to target.
    """
    ...
