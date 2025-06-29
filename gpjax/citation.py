from dataclasses import (
    dataclass,
    fields,
)
from functools import singledispatch

from beartype.typing import (
    Dict,
    Union,
)

try:
    # safely removable once jax>=0.6.0
    from jaxlib.xla_extension import PjitFunction
except ModuleNotFoundError:
    from jaxlib._jax import PjitFunction

from gpjax.kernels import (
    RFF,
    ArcCosine,
    GraphKernel,
    Matern12,
    Matern32,
    Matern52,
)

CitationType = Union[None, str, Dict[str, str]]


@dataclass(repr=False)
class AbstractCitation:
    citation_key: Union[str, None] = None
    authors: Union[str, None] = None
    title: Union[str, None] = None
    year: Union[str, None] = None

    def as_str(self) -> str:
        citation_str = f"@{self.citation_type}{{{self.citation_key},"
        for field in fields(self):
            fn = field.name
            if fn not in ["citation_type", "citation_key", "notes"]:
                citation_str += f"\n{fn} = {{{getattr(self, fn)}}},"
        return citation_str + "\n}"

    def __repr__(self) -> str:
        return repr(self.as_str())

    def __str__(self) -> str:
        return self.as_str()


class NullCitation(AbstractCitation):
    def as_str(self) -> str:
        return (
            "No citation available. If you think this is an error, please open a pull"
            " request."
        )


@dataclass
class PhDThesisCitation(AbstractCitation):
    school: Union[str, None] = None
    institution: Union[str, None] = None
    citation_type: CitationType = "phdthesis"


@dataclass
class PaperCitation(AbstractCitation):
    booktitle: Union[str, None] = None
    citation_type: CitationType = "inproceedings"


@dataclass
class BookCitation(AbstractCitation):
    publisher: Union[str, None] = None
    volume: Union[str, None] = None
    citation_type: CitationType = "book"


####################
# Default citation
####################
@singledispatch
def cite(tree) -> AbstractCitation:
    return NullCitation()


####################
# Default citation
####################
@cite.register(PjitFunction)
def _(tree) -> None:
    raise RuntimeError("Citation not available for jitted objects.")


####################
# Kernel citations
####################
@cite.register(Matern12)
@cite.register(Matern32)
@cite.register(Matern52)
def _(tree) -> PhDThesisCitation:
    citation = PhDThesisCitation(
        citation_key="matern1960SpatialV",
        authors="Bertil Matérn",
        title=(
            "Spatial variation : Stochastic models and their application to some"
            " problems in forest surveys and other sampling investigations"
        ),
        year="1960",
        school="Stockholm University",
        institution="Stockholm University",
    )
    return citation


@cite.register(ArcCosine)
def _(_) -> PaperCitation:
    return PaperCitation(
        citation_key="cho2009kernel",
        authors="Cho, Youngmin and Saul, Lawrence",
        title="Kernel Methods for Deep Learning",
        year="2009",
        booktitle="Advances in Neural Information Processing Systems",
    )


@cite.register(GraphKernel)
def _(tree) -> PaperCitation:
    return PaperCitation(
        citation_key="borovitskiy2021matern",
        title="Matérn Gaussian Processes on Graphs",
        authors=(
            "Borovitskiy, Viacheslav and Azangulov, Iskander and Terenin, Alexander and"
            " Mostowsky, Peter and Deisenroth, Marc and Durrande, Nicolas"
        ),
        booktitle="International Conference on Artificial Intelligence and Statistics",
        year="2021",
    )


@cite.register(RFF)
def _(tree) -> PaperCitation:
    return PaperCitation(
        citation_key="rahimi2007random",
        authors="Rahimi, Ali and Recht, Benjamin",
        title="Random features for large-scale kernel machines",
        year="2007",
        booktitle="Advances in neural information processing systems",
        citation_type="article",
    )
