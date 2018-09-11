#coding: utf-8

__author__ = "Marcelo Medeiros de Vasconcellos"
__copyright__ = "Copyright 2018"
__email__ = "marcelomdevasconcellos@gmail.com"

"""

    eMensageriaPro - Sistema de Gerenciamento de Eventos do eSocial e EFD-Reinf <www.emensageria.com.br>
    Copyright (C) 2018  Marcelo Medeiros de Vasconcellos

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

        Este programa é distribuído na esperança de que seja útil,
        mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de
        COMERCIABILIDADE OU ADEQUAÇÃO A UM DETERMINADO FIM. Veja o
        Licença Pública Geral GNU Affero para mais detalhes.

        Este programa é software livre: você pode redistribuí-lo e / ou modificar
        sob os termos da licença GNU Affero General Public License como
        publicado pela Free Software Foundation, seja versão 3 do
        Licença, ou (a seu critério) qualquer versão posterior.

        Você deveria ter recebido uma cópia da Licença Pública Geral GNU Affero
        junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.

"""

import datetime
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from emensageriapro.padrao import *
from emensageriapro.tabelas.forms import *
from emensageriapro.tabelas.models import *
from emensageriapro.controle_de_acesso.models import *
import base64

#IMPORTACOES


def apagar(request, hash):
    db_slug = 'default'
    try:
        usuario_id = request.session['usuario_id']
        dict_hash = get_hash_url( hash )
        financiamentos_aposentadorias_especiais_id = int(dict_hash['id'])
        for_print = int(dict_hash['print'])
    except:
        usuario_id = False
        return redirect('login')
    usuario = get_object_or_404(Usuarios.objects.using( db_slug ), excluido = False, id = usuario_id)
    pagina = ConfigPaginas.objects.using( db_slug ).get(excluido = False, endereco='financiamentos_aposentadorias_especiais')
    permissao = ConfigPermissoes.objects.using( db_slug ).get(excluido = False, config_paginas=pagina, config_perfis=usuario.config_perfis)

    dict_permissoes = json_to_dict(usuario.config_perfis.permissoes)
    paginas_permitidas_lista = usuario.config_perfis.paginas_permitidas
    modulos_permitidos_lista = usuario.config_perfis.modulos_permitidos

    financiamentos_aposentadorias_especiais = get_object_or_404(FinanciamentosAposentadoriasEspeciais.objects.using( db_slug ), excluido = False, id = financiamentos_aposentadorias_especiais_id)
    if request.method == 'POST':
        FinanciamentosAposentadoriasEspeciais.objects.using( db_slug ).filter(id = financiamentos_aposentadorias_especiais_id).update(excluido = True)
        #financiamentos_aposentadorias_especiais_apagar_custom
        #financiamentos_aposentadorias_especiais_apagar_custom
        messages.success(request, 'Apagado com sucesso!')
        if request.session['retorno_pagina']== 'financiamentos_aposentadorias_especiais_salvar':
            return redirect('financiamentos_aposentadorias_especiais', hash=request.session['retorno_hash'])
        else:
            return redirect(request.session['retorno_pagina'], hash=request.session['retorno_hash'])
    context = {
        'usuario': usuario,
   
        'modulos_permitidos_lista': modulos_permitidos_lista,
        'paginas_permitidas_lista': paginas_permitidas_lista,
   
        'permissao': permissao,
        'data': datetime.datetime.now(),
        'pagina': pagina,
        'dict_permissoes': dict_permissoes,
        'hash': hash,
    }
    return render(request, 'financiamentos_aposentadorias_especiais_apagar.html', context)

def render_to_pdf(template_src, context_dict={}):
    from io import BytesIO
    from django.http import HttpResponse
    from django.template.loader import get_template
    from xhtml2pdf import pisa
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def json_search(request, search):
    from django.http import JsonResponse
    import operator
    from django.db.models import Count, Q
    import urllib
    db_slug = 'default'
    search = urllib.unquote(search)
    lista = search.split(" ")
    dicionario = {}
    if search.strip():
        try:
            query = reduce(operator.and_, ((Q(titulo__icontains=item) | Q(codigo__icontains=item)) for item in lista))
            lista = FinanciamentosAposentadoriasEspeciais.objects.using(db_slug).filter(excluido = False).filter(query).all()
        except:
            query = reduce(operator.and_, ((Q(descricao__icontains=item) | Q(codigo__icontains=item)) for item in lista))
            lista = FinanciamentosAposentadoriasEspeciais.objects.using(db_slug).filter(excluido = False).filter(query).all()
    else:
        lista = FinanciamentosAposentadoriasEspeciais.objects.using(db_slug).filter(excluido=False).all()
    lista_financiamentos_aposentadorias_especiais = []
    for a in lista:
        dic = {}
        dic['key'] = a.codigo
        dic['value'] = '%s' % (a)
        lista_financiamentos_aposentadorias_especiais.append(dic)
    dicionario['financiamentos_aposentadorias_especiais'] = lista_financiamentos_aposentadorias_especiais
    return JsonResponse(dicionario)


def listar(request, hash):
    for_print = 0
    db_slug = 'default'
    try:
        usuario_id = request.session['usuario_id']
        dict_hash = get_hash_url( hash )
        #retorno_pagina = dict_hash['retorno_pagina']
        #retorno_hash = dict_hash['retorno_hash']
        #financiamentos_aposentadorias_especiais_id = int(dict_hash['id'])
        for_print = int(dict_hash['print'])
    except:
        usuario_id = False
        return redirect('login')
    usuario = get_object_or_404(Usuarios.objects.using( db_slug ), excluido = False, id = usuario_id)
    pagina = ConfigPaginas.objects.using( db_slug ).get(excluido = False, endereco='financiamentos_aposentadorias_especiais')
    permissao = ConfigPermissoes.objects.using( db_slug ).get(excluido = False, config_paginas=pagina, config_perfis=usuario.config_perfis)
    dict_permissoes = json_to_dict(usuario.config_perfis.permissoes)
    paginas_permitidas_lista = usuario.config_perfis.paginas_permitidas
    modulos_permitidos_lista = usuario.config_perfis.modulos_permitidos

    if permissao.permite_listar:
        filtrar = False
        dict_fields = {}
        show_fields = {
            'show_excluido': 0,
            'show_modificado_por': 0,
            'show_modificado_em': 0,
            'show_criado_por': 0,
            'show_criado_em': 0,
            'show_descricao': 1,
            'show_codigo': 1, }
        post = False
        if request.method == 'POST':
            post = True
            dict_fields = {
                'descricao__icontains': 'descricao__icontains',
                'codigo__icontains': 'codigo__icontains',}
            for a in dict_fields:
                dict_fields[a] = request.POST.get(a or None)
            for a in show_fields:
                show_fields[a] = request.POST.get(a or None)
            if request.method == 'POST':
                dict_fields = {
                'descricao__icontains': 'descricao__icontains',
                'codigo__icontains': 'codigo__icontains',}
                for a in dict_fields:
                    dict_fields[a] = request.POST.get(dict_fields[a] or None)
        dict_qs = clear_dict_fields(dict_fields)
        financiamentos_aposentadorias_especiais_lista = FinanciamentosAposentadoriasEspeciais.objects.using( db_slug ).filter(**dict_qs).filter(excluido = False).exclude(id=0).all()
        if not post and len(financiamentos_aposentadorias_especiais_lista) > 100:
            filtrar = True
            financiamentos_aposentadorias_especiais_lista = None
            messages.warning(request, 'Listagem com mais de 100 resultados! Filtre os resultados um melhor desempenho!')

        #financiamentos_aposentadorias_especiais_listar_custom
        request.session["retorno_hash"] = hash
        request.session["retorno_pagina"] = 'financiamentos_aposentadorias_especiais'
        context = {
            'financiamentos_aposentadorias_especiais_lista': financiamentos_aposentadorias_especiais_lista,
       
            'usuario': usuario,
            'modulos_permitidos_lista': modulos_permitidos_lista,
            'paginas_permitidas_lista': paginas_permitidas_lista,
       
            'permissao': permissao,
            'dict_fields': dict_fields,
            'data': datetime.datetime.now(),
            'pagina': pagina,
            'dict_permissoes': dict_permissoes,
            'show_fields': show_fields,
            'for_print': for_print,
            'hash': hash,
            'filtrar': filtrar,
   
        }
        if for_print in (0,1):
            return render(request, 'financiamentos_aposentadorias_especiais_listar.html', context)
        elif for_print == 2:
            #return render_to_pdf('tables/s1000_evtinfoempregador_pdf_xls.html', context)
            from wkhtmltopdf.views import PDFTemplateResponse
            response = PDFTemplateResponse(
                request=request,
                template='financiamentos_aposentadorias_especiais_listar.html',
                filename="financiamentos_aposentadorias_especiais.pdf",
                context=context,
                show_content_in_browser=True,
                cmd_options={'margin-top': 10,
                             'margin-bottom': 10,
                             'margin-right': 10,
                             'margin-left': 10,
                             'zoom': 1,
                             'dpi': 72,
                             'orientation': 'Landscape',
                             "viewport-size": "1366 x 513",
                             'javascript-delay': 1000,
                             'footer-center': '[page]/[topage]',
                             "no-stop-slow-scripts": True},
            )
            return response
        elif for_print == 3:
            from django.shortcuts import render_to_response
            response = render_to_response('financiamentos_aposentadorias_especiais_listar.html', context)
            filename = "financiamentos_aposentadorias_especiais.xls"
            response['Content-Disposition'] = 'attachment; filename=' + filename
            response['Content-Type'] = 'application/vnd.ms-excel; charset=UTF-8'
            return response
        elif for_print == 4:
            from django.shortcuts import render_to_response
            response = render_to_response('tables/financiamentos_aposentadorias_especiais_csv.html', context)
            filename = "financiamentos_aposentadorias_especiais.csv"
            response['Content-Disposition'] = 'attachment; filename=' + filename
            response['Content-Type'] = 'text/csv; charset=UTF-8'
            return response
    else:
        context = {
            'usuario': usuario,
       
            'modulos_permitidos_lista': modulos_permitidos_lista,
            'paginas_permitidas_lista': paginas_permitidas_lista,
       
            'permissao': permissao,
            'data': datetime.datetime.now(),
            'pagina': pagina,
            'dict_permissoes': dict_permissoes,
        }
        return render(request, 'permissao_negada.html', context)

def salvar(request, hash):
    db_slug = 'default'
    try:
        usuario_id = request.session['usuario_id']
        dict_hash = get_hash_url( hash )
        financiamentos_aposentadorias_especiais_id = int(dict_hash['id'])
        if 'tab' not in dict_hash.keys():
            dict_hash['tab'] = ''
        for_print = int(dict_hash['print'])
    except:
        usuario_id = False
        return redirect('login')
    usuario = get_object_or_404(Usuarios.objects.using( db_slug ), excluido = False, id = usuario_id)
    pagina = ConfigPaginas.objects.using( db_slug ).get(excluido = False, endereco='financiamentos_aposentadorias_especiais')
    permissao = ConfigPermissoes.objects.using( db_slug ).get(excluido = False, config_paginas=pagina, config_perfis=usuario.config_perfis)
    if financiamentos_aposentadorias_especiais_id:
        financiamentos_aposentadorias_especiais = get_object_or_404(FinanciamentosAposentadoriasEspeciais.objects.using( db_slug ), excluido = False, id = financiamentos_aposentadorias_especiais_id)
    dict_permissoes = json_to_dict(usuario.config_perfis.permissoes)
    paginas_permitidas_lista = usuario.config_perfis.paginas_permitidas
    modulos_permitidos_lista = usuario.config_perfis.modulos_permitidos

    if permissao.permite_visualizar:
        mensagem = None
        if financiamentos_aposentadorias_especiais_id:
            financiamentos_aposentadorias_especiais_form = form_financiamentos_aposentadorias_especiais(request.POST or None, instance = financiamentos_aposentadorias_especiais, slug = db_slug)
        else:
            financiamentos_aposentadorias_especiais_form = form_financiamentos_aposentadorias_especiais(request.POST or None, slug = db_slug, initial={})
        if request.method == 'POST':
            if financiamentos_aposentadorias_especiais_form.is_valid():
                dados = financiamentos_aposentadorias_especiais_form.cleaned_data
                if financiamentos_aposentadorias_especiais_id:
                    dados['modificado_por_id'] = usuario_id
                    dados['modificado_em'] = datetime.datetime.now()
                    #financiamentos_aposentadorias_especiais_campos_multiple_passo1
                    FinanciamentosAposentadoriasEspeciais.objects.using(db_slug).filter(id=financiamentos_aposentadorias_especiais_id).update(**dados)
                    obj = FinanciamentosAposentadoriasEspeciais.objects.using(db_slug).get(id=financiamentos_aposentadorias_especiais_id)
                    #financiamentos_aposentadorias_especiais_editar_custom
                    #financiamentos_aposentadorias_especiais_campos_multiple_passo2
                    messages.success(request, 'Alterado com sucesso!')
                else:

                    dados['criado_por_id'] = usuario_id
                    dados['criado_em'] = datetime.datetime.now()
                    dados['excluido'] = False
                    #financiamentos_aposentadorias_especiais_cadastrar_campos_multiple_passo1
                    obj = FinanciamentosAposentadoriasEspeciais(**dados)
                    obj.save(using = db_slug)
                    #financiamentos_aposentadorias_especiais_cadastrar_custom
                    #financiamentos_aposentadorias_especiais_cadastrar_campos_multiple_passo2
                    messages.success(request, 'Cadastrado com sucesso!')
                if request.session['retorno_pagina'] not in ('financiamentos_aposentadorias_especiais_apagar', 'financiamentos_aposentadorias_especiais_salvar', 'financiamentos_aposentadorias_especiais'):
                    return redirect(request.session['retorno_pagina'], hash=request.session['retorno_hash'])
                if financiamentos_aposentadorias_especiais_id != obj.id:
                    url_hash = base64.urlsafe_b64encode( '{"print": "0", "id": "%s"}' % (obj.id) )
                    return redirect('financiamentos_aposentadorias_especiais_salvar', hash=url_hash)
            else:
                messages.error(request, 'Erro ao salvar!')
        financiamentos_aposentadorias_especiais_form = disabled_form_fields(financiamentos_aposentadorias_especiais_form, permissao.permite_editar)
        #financiamentos_aposentadorias_especiais_campos_multiple_passo3

        for field in financiamentos_aposentadorias_especiais_form.fields.keys():
            financiamentos_aposentadorias_especiais_form.fields[field].widget.attrs['ng-model'] = 'financiamentos_aposentadorias_especiais_'+field
        if int(dict_hash['print']):
            financiamentos_aposentadorias_especiais_form = disabled_form_for_print(financiamentos_aposentadorias_especiais_form)
        #[VARIAVEIS_SECUNDARIAS_VAZIAS]
        if financiamentos_aposentadorias_especiais_id:
            financiamentos_aposentadorias_especiais = get_object_or_404(FinanciamentosAposentadoriasEspeciais.objects.using( db_slug ), excluido = False, id = financiamentos_aposentadorias_especiais_id)
            pass
        else:
            financiamentos_aposentadorias_especiais = None
        #financiamentos_aposentadorias_especiais_salvar_custom_variaveis#
        tabelas_secundarias = []
        #[FUNCOES_ESPECIAIS_SALVAR]
        if dict_hash['tab'] or 'financiamentos_aposentadorias_especiais' in request.session['retorno_pagina']:
            request.session["retorno_hash"] = hash
            request.session["retorno_pagina"] = 'financiamentos_aposentadorias_especiais_salvar'
        context = {
            'financiamentos_aposentadorias_especiais': financiamentos_aposentadorias_especiais,
            'financiamentos_aposentadorias_especiais_form': financiamentos_aposentadorias_especiais_form,
            'mensagem': mensagem,
            'financiamentos_aposentadorias_especiais_id': int(financiamentos_aposentadorias_especiais_id),
            'usuario': usuario,
       
            'hash': hash,
            #[VARIAVEIS_SECUNDARIAS]
            'modulos_permitidos_lista': modulos_permitidos_lista,
            'paginas_permitidas_lista': paginas_permitidas_lista,
       
            'permissao': permissao,
            'data': datetime.datetime.now(),
            'pagina': pagina,
            'dict_permissoes': dict_permissoes,
            'for_print': int(dict_hash['print']),
            'tabelas_secundarias': tabelas_secundarias,
            'tab': dict_hash['tab'],
            #financiamentos_aposentadorias_especiais_salvar_custom_variaveis_context#
        }
        if for_print in (0,1 ):
            return render(request, 'financiamentos_aposentadorias_especiais_salvar.html', context)
        elif for_print == 2:
            from wkhtmltopdf.views import PDFTemplateResponse
            response = PDFTemplateResponse(
                request=request,
                template='financiamentos_aposentadorias_especiais_salvar.html',
                filename="financiamentos_aposentadorias_especiais.pdf",
                context=context,
                show_content_in_browser=True,
                cmd_options={'margin-top': 10,
                             'margin-bottom': 10,
                             'margin-right': 10,
                             'margin-left': 10,
                             'zoom': 1,
                             'dpi': 72,
                             'orientation': 'Landscape',
                             "viewport-size": "1366 x 513",
                             'javascript-delay': 1000,
                             'footer-center': '[page]/[topage]',
                             "no-stop-slow-scripts": True},
            )
            return response
        elif for_print == 3:
            from django.shortcuts import render_to_response
            response = render_to_response('financiamentos_aposentadorias_especiais_salvar.html', context)
            filename = "financiamentos_aposentadorias_especiais.xls"
            response['Content-Disposition'] = 'attachment; filename=' + filename
            response['Content-Type'] = 'application/vnd.ms-excel; charset=UTF-8'
            return response

    else:
        context = {
            'usuario': usuario,
       
            'modulos_permitidos_lista': modulos_permitidos_lista,
            'paginas_permitidas_lista': paginas_permitidas_lista,
       
            'permissao': permissao,
            'data': datetime.datetime.now(),
            'pagina': pagina,
            'dict_permissoes': dict_permissoes,
        }
        return render(request, 'permissao_negada.html', context)
