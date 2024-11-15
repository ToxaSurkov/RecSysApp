"""
File: instruction.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Project instructions for the Gradio app.
License: MIT License
"""

# Importing necessary components for the Gradio app

INSTRUCTION_TEXT = """\
<div class="instructions">
    <p>Вам предстоит анонимно оценить качество приложения EdFitter – новой рекомендательной системы, которая советует студентам выборные курсы исходя из их карьерных запросов.</p>
    <ul>
        <li>На следующем экране введите запрос в форме <span>ищу вакансию [название профессии]</span> по вашему желанию. Будьте реалистичны и вводите название профессии, на которую вы можете претендовать с учетом вашей программы обучения.</li>
        <li>В списке отобразившихся навыков кликните все, которые кажутся вам ЛИШНИМИ, НЕРЕЛЕВАНТНЫМИ вашему запросу.</li>
        <li>Напротив каждого курса оцените его соответствие вашему запросу по смыслу по семибалльной шкале, где <span>1</span> – совсем не подходит, <span>7</span> – отлично подходит.</li>
        <li>Прокрутите страницу и введите в первое поле отсутствующие в выдаче навыки, которые считаете важными для вакансии.</li>
        <li>Затем ответьте на четыре вопроса о приложении в целом. В вопросах со шкалами <span>1</span> означает совсем неудобно / неполезно, <span>7</span> - очень удобно / полезно.</li>
        <li>У вас также будет возможность отметить лишние навыки в курсах и ввести в последнее поле требуемые в вакансии навыков, которых в курсах не нашлось.</li>
        <li>Нажмите на кнопку <span>сохранить ответы</span> и повторите все действия (кроме ответов на вопросы о приложении), на этот раз сформулировав запрос в свободной форме (например, <span>хочу работать в сфере IT</span>).</li>
        <li>Вы можете на этом закончить работу или повторить все действия сколько угодно раз, в том числе изменть свое мнение о приложении.</li>
        <li>По окончании работы снова нажмите кнопку <span>сохранить ответы</span> и закройте страницу браузера.</li>
    </ul>
</div>
"""