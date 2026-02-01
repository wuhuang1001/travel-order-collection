# check_deps.py
from importlib.metadata import version, PackageNotFoundError
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet


def check_requirements(requirements_file='requirements.txt'):
    with open(requirements_file, 'r') as f:
        requirements = f.read().splitlines()

    errors = []
    for req in requirements:
        req = req.strip()
        if not req or req.startswith('#'):
            continue

        try:
            # 使用 packaging 解析需求
            requirement = Requirement(req)
            pkg_name = requirement.name
            installed_version = version(pkg_name)

            # 验证版本是否满足规范
            if requirement.specifier and not requirement.specifier.contains(installed_version):
                errors.append(
                    f"{pkg_name}: 已安装 {installed_version}, 要求 {requirement.specifier}"
                )
            # 无版本要求的包不做检查
        except PackageNotFoundError:
            errors.append(f"{req.split('<')[0].split('>')[0].split('=')[0].split('!')[0].strip()} (未安装)")
        except Exception as e:
            errors.append(f"{req} (解析错误: {e})")

    if errors:
        print(f"依赖问题:\n" + "\n".join(f"  - {e}" for e in errors))
        return False
    return True
