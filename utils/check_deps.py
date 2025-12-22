# check_deps.py
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict

def check_requirements(requirements_file='requirements.txt'):
    with open(requirements_file, 'r') as f:
        requirements = f.read().splitlines()

    try:
        pkg_resources.require(requirements) # type: ignore
        # print("所有依赖项均已满足。")
        return True
    except (DistributionNotFound, VersionConflict) as e:
        print(f"依赖缺失或可能存在的版本冲突: \n{e}")
        return False

